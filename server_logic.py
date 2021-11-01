import random
from typing import List, Dict


def avoid_body(my_head: Dict[str, int], my_body: List[Dict[str, int]], possible_moves: List[str]) -> List[str]:
    for body_part in my_body[1:]:  # Exclude head from body

        # this body part is left of my head
        if body_part["x"] < my_head["x"] and body_part["y"] == my_head["y"] and "left" in possible_moves:
            print("Removed left")
            possible_moves.remove("left")

        # this body part is right of my head
        elif body_part["x"] > my_head["x"] and body_part["y"] == my_head["y"] and "right" in possible_moves:
            print("Removed right")
            possible_moves.remove("right")

        # this body part is below my head
        elif body_part["y"] < my_head["y"] and body_part["x"] == my_head["x"] and "down" in possible_moves:
            print("Removed down")
            possible_moves.remove("down")

        # this body part is above my head
        elif body_part["y"] > my_head["y"] and body_part["x"] == my_head["x"] and "up" in possible_moves:
            print("Removed up")
            possible_moves.remove("up")

    return possible_moves


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
        return random.choice(possible_moves)


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
    food = board["food"][0]  # Make a b-line for the first meal that appears
    possible_moves = ["up", "down", "left", "right"]

    print(f"HEAD x:{my_head['x']}, y:{my_head['y']}")
    print(f"FOOD x:{food['x']}, y:{food['y']}")

    possible_moves = avoid_body(my_head, my_body, possible_moves)
    possible_moves = avoid_walls(my_head, board, possible_moves)

    # Pick a move based on where the scooby snacks are
    move = travel_to_food(my_head, food, possible_moves)

    print(f"Turn #{data['turn']}: {move} picked from all valid options in {possible_moves}\n")

    return move
