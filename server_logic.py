import random
from typing import List, Dict


def print_function(func):
    def inner(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return inner


@print_function
def avoid_body(my_head: Dict[str, int], my_body: List[Dict[str, int]], possible_moves: List[str]) -> List[str]:
    for body_part in my_body[1:]:  # Exclude head from body
        body_x = body_part["x"]
        body_y = body_part["y"]

        head_x = my_head["x"]
        head_y = my_head["y"]

        # This body part is left of my head
        if body_x - head_x == -1 and body_y == head_y and "left" in possible_moves:
            print("Removed left")
            possible_moves.remove("left")

        # This body part is right of my head
        elif body_x - head_x == 1 and body_y == head_y and "right" in possible_moves:
            print("Removed right")
            possible_moves.remove("right")

        # This body part is below my head
        elif body_y - head_y == -1 and body_x == head_x and "down" in possible_moves:
            print("Removed down")
            possible_moves.remove("down")

        # This body part is above my head
        elif body_y - head_y == 1 and body_x == head_x and "up" in possible_moves:
            print("Removed up")
            possible_moves.remove("up")

    return possible_moves


@print_function
def avoid_walls(my_head: Dict[str, int], board: Dict[str, int], possible_moves: List[str]) -> List[str]:
    if my_head["x"] == (board["width"] - 1) and "right" in possible_moves:  # Wall is to the right of the head
        print("Removed right")
        possible_moves.remove("right")

    if my_head["x"] == 0 and "left" in possible_moves:  # Wall is to the left of the head
        print("Removed left")
        possible_moves.remove("left")

    if my_head["y"] == (board["height"] - 1) and "up" in possible_moves:  # Wall is above the head
        print("Removed up")
        possible_moves.remove("up")

    if my_head["y"] == 0 and "down" in possible_moves:  # Wall is below the head
        print("Removed down")
        possible_moves.remove("down")

    return possible_moves


@print_function
def travel_to_food(my_head: Dict[str, int], food: Dict[str, int], possible_moves: List[str]) -> str:
    # Food is to the right of the head
    if my_head["x"] < food["x"] and "right" in possible_moves:
        return "right"

    # Food is to the left of the head
    elif my_head["x"] > food["x"] and "left" in possible_moves:
        return "left"

    # Food is above the head
    elif my_head["y"] < food["y"] and "up" in possible_moves:
        return "up"

    # Food is below the head
    elif my_head["y"] > food["y"] and "down" in possible_moves:
        return "down"

    # Allah-akbar
    else:
        try:
            return random.choice(possible_moves)
        except IndexError:  # There are no valid moves left
            print("Allah-akbar")
            return "up"


@print_function
def calculate_nearest_food(my_head: Dict[str, int], all_food: List[Dict[str, int]]) -> Dict[str, int]:
    def calculate_tiles_to_food(this_food: Dict[str, int]) -> int:
        tiles = 0
        this_food_x = this_food["x"]
        this_food_y = this_food["y"]

        tiles += head_x - this_food_x if head_x > this_food_x else this_food_x - head_x
        tiles += head_y - this_food_y if head_y > this_food_y else this_food_y - head_y

        return tiles

    result = all_food[0]
    head_x = my_head["x"]
    head_y = my_head["y"]

    result_tiles = calculate_tiles_to_food(all_food[0])

    for food in all_food[1:]:
        if calculate_tiles_to_food(food) < result_tiles:
            result = food

    return result


@print_function
def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request
    return: A String, the single move to make. One of "up", "down", "left" or "right".
    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.
    """

    my_head = data["you"]["head"]
    my_body = data["you"]["body"]
    board = data["board"]
    all_food = board["food"]
    possible_moves = ["up", "down", "left", "right"]

    print(f"HEAD x:{my_head['x']}, y:{my_head['y']}")

    possible_moves = avoid_body(my_head, my_body, possible_moves)
    possible_moves = avoid_walls(my_head, board, possible_moves)

    food = calculate_nearest_food(my_head, all_food)

    print(f"FOOD x:{food['x']}, y:{food['y']}")

    # Pick a move based on where the scooby snack is
    move = travel_to_food(my_head, food, possible_moves)

    print(f"Turn #{data['turn']}: {move} picked from all valid options in {possible_moves}\n")

    return move
