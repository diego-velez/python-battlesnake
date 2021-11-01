import os

from flask import Flask
from flask import request

import server_logic


app = Flask(__name__)
DEBUG = True


@app.get("/")
def handle_info():
    print("INFO request")

    return {
        "apiversion": "1",
        "author": "DVT",
        "color": "#FF00FF",
        "head": "beluga",
        "tail": "bolt",
    }


@app.post("/start")
def handle_start():
    """
    This function is called everytime your snake is entered into a game.
    request.json contains information about the game that's about to be played.
    """
    data = request.get_json()

    print(f"NEW GAME START (id:{data['game']['id']})")
    return "ok"


@app.post("/move")
def handle_move():
    """
    This function is called on every turn of a game. It's how your snake decides where to move.
    Valid moves are "up", "down", "left", or "right".
    """
    data = request.get_json()

    # TODO - look at the server_logic.py file to see how we decide what move to return!
    move = server_logic.choose_move(data)

    return {"move": move}


@app.post("/end")
def end():
    data = request.get_json()

    print(f"GAME OVER (id:{data['game']['id']})")
    return "ok"


if __name__ == "__main__":
    print("Starting Battlesnake Server")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
