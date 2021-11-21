import logging
import random
import time
from collections import namedtuple
from typing import List
import datetime

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
COORDINATE = namedtuple('coordinate', ('x', 'y'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(funcName)s:%(message)s')


class Snake:
    possible_moves = [
        LEFT, RIGHT,
        DOWN, UP
    ]
    nearest_food = None
    all_moves = list()

    def __init__(self, data: dict):
        self.set_data(data)

        file_handler = logging.FileHandler(f'{datetime.datetime.now()}: {self.gamemode} game.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info('Game start\n')

    def __set_game(self, game: dict):
        self.game_id = game["id"]
        self.gamemode = game["ruleset"]["name"]
        self.gamemode_version = game["ruleset"]["version"]
        self.max_latency = game["timeout"]

    def __set_you(self, you: dict):
        self.snake_id = you["id"]
        self.name = you["name"]
        self.health = you["health"]
        self.body = [COORDINATE(**part) for part in you["body"][1:]]
        self.latency = you["latency"]
        self.head = COORDINATE(**you["head"])
        self.length = you["length"]
        self.shout = you["shout"]
        self.squad = you["squad"]

    def __set_board(self, board: dict):
        self.height = board["height"]
        self.width = board["width"]
        self.all_food = board["food"]
        self.hazards = [COORDINATE(**hazard) for hazard in board["hazards"]]
        self.enemies = board["snakes"][1:]  # Exclude myself

    """
        Must be called before calling choose_move, in order to choose a move based on the current board
    """
    def set_data(self, data: dict):
        self.__set_game(data["game"])
        self.__set_you(data["you"])
        self.turn = data["turn"]
        self.__set_board(data["board"])

    """
        Makes all moves available to the snake
    """
    def __reset_moves(self):
        logger.debug('Reset Moves')
        self.possible_moves = [
            LEFT, RIGHT,
            DOWN, UP
        ]

    def __avoid_walls(self, simulated_head: COORDINATE):
        # Wall is to the right of my head
        if simulated_head.x == (self.width - 1) and RIGHT in self.possible_moves:  # Wall is to the right of the head
            logger.debug("Removed right")
            self.possible_moves.remove(RIGHT)

        # Wall is to the left of my head
        if simulated_head.x == 0 and LEFT in self.possible_moves:  # Wall is to the left of the head
            logger.debug("Removed left")
            self.possible_moves.remove(LEFT)

        # Wall is above my head
        if simulated_head.y == (self.height - 1) and UP in self.possible_moves:  # Wall is above the head
            logger.debug("Removed up")
            self.possible_moves.remove(UP)

        # Wall is below my head
        if simulated_head.y == 0 and DOWN in self.possible_moves:  # Wall is below the head
            logger.debug("Removed down")
            self.possible_moves.remove(DOWN)

    def __avoid_collision(self, simulated_head: COORDINATE, collisions: List[COORDINATE]):
        for collision in collisions:
            # This collision is to the left of my head
            if collision.x - simulated_head.x == -1 and collision.y == simulated_head.y and LEFT in self.possible_moves:
                logger.debug("Removed left")
                self.possible_moves.remove(LEFT)

            # This collision is to the right of my head
            elif collision.x - simulated_head.x == 1 and collision.y == simulated_head.y and RIGHT in self.possible_moves:
                logger.debug("Removed right")
                self.possible_moves.remove(RIGHT)

            # This collision is below my head
            elif collision.y - simulated_head.y == -1 and collision.x == simulated_head.x and DOWN in self.possible_moves:
                logger.debug("Removed down")
                self.possible_moves.remove(DOWN)

            # This collision is above my head
            elif collision.y - simulated_head.y == 1 and collision.x == simulated_head.x and UP in self.possible_moves:
                logger.debug("Removed up")
                self.possible_moves.remove(UP)

    def __avoid_all_obstacles(self, simulated_head: COORDINATE = None, simulated_body: List[COORDINATE] = None):
        if simulated_head is None:
            simulated_head = self.head
        if simulated_body is None:
            simulated_body = self.body

        self.__avoid_walls(simulated_head)

        # Make sure head does not collide with its own body
        self.__avoid_collision(simulated_head, simulated_body)

        # Avoid enemies if there are any
        if len(self.enemies) > 0:
            for enemy in self.enemies:
                enemy_body = [COORDINATE(**body_part) for body_part in enemy['body']]
                self.__avoid_collision(simulated_head, enemy_body)

        # Avoid hazards if there are any
        if len(self.hazards) > 0:
            self.__avoid_collision(simulated_head, self.hazards)

    """
        Calculates nearest food based on the tiles it takes from the head to the food
        
        If it cannot calculate the tiles it takes to get to the food it skips that food, or if it could not calculate
        the amount of tiles it takes to get to any food, then it calls __choose_next_move
    """
    def __calculate_nearest_food(self):
        def calculate_tiles_to_food() -> List[str] or None:
            all_moves_to_food = list()
            simulated_head = self.head  # Keep track of where the head will be based on all the moves
            simulated_body = advance_body(simulated_head, self.body)

            # Runs loop until the head reaches the food
            while simulated_head != food:
                self.__reset_moves()
                self.__avoid_all_obstacles(simulated_head, simulated_body)
                move = travel_to_food(all_moves_to_food, simulated_head)

                # Could not calculate path to food
                if move is None:
                    return move

                all_moves_to_food.append(move)
                simulated_head = head_coord_based_on_move(move, simulated_head)
                simulated_body = advance_body(simulated_head, simulated_body)

            return all_moves_to_food

        """
            Chooses the next move of the head based on the position of the food and the moves the head can make
            without killing itself
        """
        def travel_to_food(all_moves: List[str], head: COORDINATE) -> str or None:

            """
                Returns the opposite move of the move passed
            """
            def opposite_move(move: str) -> str:
                if move == RIGHT:
                    return LEFT
                elif move == LEFT:
                    return RIGHT
                elif move == UP:
                    return DOWN
                elif move == DOWN:
                    return UP

            # I will die no matter what move I do
            if len(self.possible_moves) == 0:
                logger.error(f'Death is inevitable')
                return UP

            """
                Removes the opposite move, of the previous move, from being chosen as the next move
                
                Fixes bug where __calculate_nearest_food would keep choosing two opposing moves indefinitely
            """
            if len(all_moves) > 0:
                opposite_move = opposite_move(all_moves[-1])

                if opposite_move in self.possible_moves:
                    self.possible_moves.remove(opposite_move)

            result = None
            # Food is to the right of the head
            if head.x < food.x and RIGHT in self.possible_moves:
                result = RIGHT

            # Food is to the left of the head
            elif head.x > food.x and LEFT in self.possible_moves:
                result = LEFT

            # Food is above the head
            elif head.y < food.y and UP in self.possible_moves:
                result = UP

            # Food is below the head
            elif head.y > food.y and DOWN in self.possible_moves:
                result = DOWN

            # Could not find a direct path to the food
            if result is None:
                logger.warning(f'Could not find a clear way to food at {food}')
                return result

            logger.debug(f'Chose {result} move')
            return result

        """
            Returns the next coordinates of the head based on the move chosen
        """
        def head_coord_based_on_move(move: str, simulated_head: COORDINATE) -> COORDINATE:
            if move == UP:
                return COORDINATE(simulated_head.x, simulated_head.y + 1)
            elif move == DOWN:
                return COORDINATE(simulated_head.x, simulated_head.y - 1)
            elif move == LEFT:
                return COORDINATE(simulated_head.x - 1, simulated_head.y)
            elif move == RIGHT:
                return COORDINATE(simulated_head.x + 1, simulated_head.y)

        """
            Returns a list of the coordinates of the body of the snake in the next turn
        """
        def advance_body(head: COORDINATE, body: List[COORDINATE]) -> List[COORDINATE]:
            return [
                head if index == 0 else body[index - 1]
                for index in range(len(body))
            ]

        shortest_distance_to_food = None
        for food in self.all_food:
            logger.debug(f'Calculating tiles to food at {food}')

            food = COORDINATE(**food)
            moves = calculate_tiles_to_food()

            # Skip food since a path to it could not be calculated
            if moves is None:
                logger.debug(f'Skipped food at {food}')
                continue

            tiles_to_food = len(moves)

            logger.debug(f'Food at {food} is {tiles_to_food} tiles from head')

            # Check if this food is closer to the head than the previous closest food
            if shortest_distance_to_food is None or tiles_to_food < shortest_distance_to_food:
                logger.debug('Chose this food ^ as nearest')

                self.nearest_food = food
                self.all_moves = moves
                shortest_distance_to_food = tiles_to_food
        else:
            # Check if a path to any food was calculated, if not then call __choose_next_move
            if len(self.all_moves) == 0:
                logger.debug('Could not calculate a path to any food based on food')
                self.__choose_next_move()

    """
        Chooses a move that won't get the snake killed
    """
    def __choose_next_move(self):
        self.__reset_moves()
        self.__avoid_all_obstacles()

        """
            Choose a move that won't get the snake killed
            
            IndexError is thrown when self.possible_moves is empty, aka when you're going to die no matter what
        """
        try:
            self.all_moves = [random.choice(self.possible_moves)]
        except IndexError:
            self.all_moves = [UP]

    def __choose_move(self) -> str:
        logger.info(f"Starting turn #{self.turn}")
        logger.debug(f"Head is at {self.head}")

        start_time = time.time()

        """
            Go towards food if there is food and path already calculated to it,
            if there isn't a path calculated to the nearest food, then calculate it.
            
            If there isn't any food in the board then choose a move that won't kill the snake
        """
        if len(self.all_food) > 0:
            self.__calculate_nearest_food()

            logger.debug(f"Nearest food is at {self.nearest_food}")
        else:
            self.__choose_next_move()

        move = self.all_moves.pop(0)  # Move according to the previously calculated path

        logger.info(f"Chose {move} ({len(self.all_moves)} moves left)")
        self.__reset_moves()  # Must reset moves to have all moves available next turn
        logger.info(f'Took {round((time.time() - start_time) * 1000, 3)} milliseconds to complete\n')

        return move

    def choose_move(self) -> str:
        try:
            move = self.__choose_move()
        except:
            logger.exception('Unexpected Crash')
            move = UP

        return move
