import os

from flask import Flask
from flask import request

import server_logic


app = Flask(__name__)
DEBUG = True
snake = None


@app.get("/")
def handle_info():
    print("INFO request")

    return {
        "apiversion": "1",
        "author": "diego-velez",
        "color": "#FF00FF",
        "head": "beluga",
        "tail": "bolt",
    }


@app.post("/start")
def handle_start():
    data = request.get_json()

    print(f"\nNEW GAME START (id:{data['game']['id']})")
    return "ok"


@app.post("/move")
def handle_move():
    global snake

    data = request.get_json()

    if snake is None:
        snake = server_logic.Snake(data)

    snake.set_data(data)
    move = snake.choose_move()
    return {"move": move}


@app.post("/end")
def end():
    data = request.get_json()

    print(f"\nGAME OVER (id:{snake.game_id})")
    return "ok"


if __name__ == "__main__":
    print("Starting Battlesnake Server")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
