import random
import time
from typing import List, Dict
import logging
from collections import namedtuple

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

    def __init__(self, data: dict):
        self.set_data(data)

        file_handler = logging.FileHandler(f'Game (id={self.game_id}).log')
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
        self.body = you["body"][1:]
        self.latency = you["latency"]
        self.head = COORDINATE(you["head"]["x"], you["head"]["y"])
        self.length = you["length"]
        self.shout = you["shout"]
        self.squad = you["squad"]

    def __set_board(self, board: dict):
        self.height = board["height"]
        self.width = board["width"]
        self.all_food = board["food"]
        self.hazards = board["hazards"]
        self.enemies = board["snakes"][1:]  # Exclude myself

    def set_data(self, data: dict):
        self.__set_game(data["game"])
        self.__set_you(data["you"])
        self.turn = data["turn"]
        self.__set_board(data["board"])

    def __reset_moves(self):
        logger.debug('Reset Moves')
        self.possible_moves = [
            LEFT, RIGHT,
            DOWN, UP
        ]

    def __avoid_walls(self):
        if self.head.x == (self.width - 1) and RIGHT in self.possible_moves:  # Wall is to the right of the head
            logger.debug("Removed right")
            self.possible_moves.remove(RIGHT)

        if self.head.x == 0 and LEFT in self.possible_moves:  # Wall is to the left of the head
            logger.debug("Removed left")
            self.possible_moves.remove(LEFT)

        if self.head.y == (self.height - 1) and UP in self.possible_moves:  # Wall is above the head
            logger.debug("Removed up")
            self.possible_moves.remove(UP)

        if self.head.y == 0 and DOWN in self.possible_moves:  # Wall is below the head
            logger.debug("Removed down")
            self.possible_moves.remove(DOWN)

    def __avoid_collision(self, collisions: List[Dict[str, int]]):
        for collision in collisions:
            collision = COORDINATE(**collision)

            # This collision is left of my head
            if collision.x - self.head.x == -1 and collision.y == self.head.y and LEFT in self.possible_moves:
                logger.debug("Removed left")
                self.possible_moves.remove(LEFT)

            # This collision is right of my head
            elif collision.x - self.head.x == 1 and collision.y == self.head.y and RIGHT in self.possible_moves:
                logger.debug("Removed right")
                self.possible_moves.remove(RIGHT)

            # This collision is below my head
            elif collision.y - self.head.y == -1 and collision.x == self.head.x and DOWN in self.possible_moves:
                logger.debug("Removed down")
                self.possible_moves.remove(DOWN)

            # This collision is above my head
            elif collision.y - self.head.y == 1 and collision.x == self.head.x and UP in self.possible_moves:
                logger.debug("Removed up")
                self.possible_moves.remove(UP)

    def __avoid_all_obstacles(self):
        self.__avoid_walls()
        self.__avoid_collision(self.body)

        if self.gamemode != "solo":
            for enemy in self.enemies:
                self.__avoid_collision(enemy["body"])

            self.__avoid_collision(self.hazards)

    def __calculate_nearest_food(self):
        def calculate_tiles_to_food() -> int:
            logger.debug(f'Calculating tiles to food at {food}')

            tiles = 0

            tiles += self.head.x - food.x if self.head.x > food.x else food.x - self.head.x
            tiles += self.head.y - food.y if self.head.y > food.y else food.y - self.head.y

            return tiles

        result_tiles = None
        for food in self.all_food:
            food = COORDINATE(**food)
            tiles_to_food = calculate_tiles_to_food()

            logger.debug(f'Food at {food} is {tiles_to_food} tiles from head')

            if result_tiles is None or tiles_to_food < result_tiles:
                logger.debug('Chose this food ^ as nearest')

                self.nearest_food = food
                result_tiles = tiles_to_food

    def __travel_to_food(self) -> str:

        if len(self.possible_moves) == 0:
            logger.error(f'Death is inevitable')
            return UP

        # Food is to the right of the head
        if self.head.x < self.nearest_food.x and RIGHT in self.possible_moves:
            return RIGHT

        # Food is to the left of the head
        elif self.head.x > self.nearest_food.x and LEFT in self.possible_moves:
            return LEFT

        # Food is above the head
        elif self.head.y < self.nearest_food.y and UP in self.possible_moves:
            return UP

        # Food is below the head
        elif self.head.y > self.nearest_food.y and DOWN in self.possible_moves:
            return DOWN

        else:
            logger.warning(f'Could not find a clear way to food at {self.nearest_food}')
            return random.choice(self.possible_moves)

    def choose_move(self) -> str:
        logger.info(f"Starting turn #{self.turn}")
        logger.debug(f"Head is at {self.head}")

        start_time = time.time()

        self.__avoid_all_obstacles()

        if self.gamemode in ["solo", "standard"]:
            self.__calculate_nearest_food()
            move = self.__travel_to_food()

            logger.debug(f"Nearest food is at {self.nearest_food}")

        logger.info(f"Chose {move} from {self.possible_moves}")
        self.__reset_moves()
        logger.info(f'Took {round((time.time() - start_time) * 1000, 3)} milliseconds to complete\n')

        return move
