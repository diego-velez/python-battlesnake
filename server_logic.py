import random
from typing import List, Dict
import logging

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"

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

    def __avoid_walls(self):
        if self.head_x == (self.width - 1) and RIGHT in self.possible_moves:  # Wall is to the right of the head
            logger.debug("Removed right")
            self.possible_moves.remove(RIGHT)

        if self.head_x == 0 and LEFT in self.possible_moves:  # Wall is to the left of the head
            logger.debug("Removed left")
            self.possible_moves.remove(LEFT)

        if self.head_y == (self.height - 1) and UP in self.possible_moves:  # Wall is above the head
            logger.debug("Removed up")
            self.possible_moves.remove(UP)

        if self.head_y == 0 and DOWN in self.possible_moves:  # Wall is below the head
            logger.debug("Removed down")
            self.possible_moves.remove(DOWN)

    def __avoid_collision(self, collisions: List[Dict[str, int]]):
        for collision in collisions:
            collision_x = collision["x"]
            collision_y = collision["y"]

            # This collision is left of my head
            if collision_x - self.head_x == -1 and collision_y == self.head_y and LEFT in self.possible_moves:
                logger.debug("Removed left")
                self.possible_moves.remove(LEFT)

            # This collision is right of my head
            elif collision_x - self.head_x == 1 and collision_y == self.head_y and RIGHT in self.possible_moves:
                logger.debug("Removed right")
                self.possible_moves.remove(RIGHT)

            # This collision is below my head
            elif collision_y - self.head_y == -1 and collision_x == self.head_x and DOWN in self.possible_moves:
                logger.debug("Removed down")
                self.possible_moves.remove(DOWN)

            # This collision is above my head
            elif collision_y - self.head_y == 1 and collision_x == self.head_x and UP in self.possible_moves:
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
        def calculate_tiles_to_food(this_food: Dict[str, int]) -> int:
            tiles = 0
            this_food_x = this_food["x"]
            this_food_y = this_food["y"]

            tiles += self.head_x - this_food_x if self.head_x > this_food_x else this_food_x - self.head_x
            tiles += self.head_y - this_food_y if self.head_y > this_food_y else this_food_y - self.head_y

            return tiles

        self.nearest_food = self.all_food[0]

        result_tiles = calculate_tiles_to_food(self.nearest_food)

        for food in self.all_food[1:]:
            if calculate_tiles_to_food(food) < result_tiles:
                self.nearest_food = food

    def __travel_to_food(self) -> str:

        # Death is inevitable
        if len(self.possible_moves) == 0:
            return UP

        # Food is to the right of the head
        if self.head_x < self.nearest_food["x"] and RIGHT in self.possible_moves:
            return RIGHT

        # Food is to the left of the head
        elif self.head_x > self.nearest_food["x"] and LEFT in self.possible_moves:
            return LEFT

        # Food is above the head
        elif self.head_y < self.nearest_food["y"] and UP in self.possible_moves:
            return UP

        # Food is below the head
        elif self.head_y > self.nearest_food["y"] and DOWN in self.possible_moves:
            return DOWN

        # There is no clear way to the food
        else:
            return random.choice(self.possible_moves)

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
        self.head_x = you["head"]["x"]
        self.head_y = you["head"]["y"]
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

    def choose_move(self) -> str:
        logger.info(f"Starting turn #{self.turn}")
        logger.debug(f"HEAD x:{self.head_x}, y:{self.head_y}")

        self.__avoid_all_obstacles()

        if self.gamemode in ["solo", "standard"]:
            self.__calculate_nearest_food()
            move = self.__travel_to_food()

            logger.debug(f"FOOD x:{self.nearest_food['x']}, y:{self.nearest_food['y']}")

        logger.info(f"Chose {move} from {self.possible_moves}\n")

        self.possible_moves = [
            LEFT, RIGHT,
            DOWN, UP
        ]

        return move
