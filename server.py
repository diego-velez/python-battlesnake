import os

from flask import Flask
from flask import request

from snake import Snake

app = Flask(__name__)
snake: Snake = None


@app.get("/")
def handle_info():
    return {
        "apiversion": "1",
        "author": "diego-velez",
        "color": "#FF00FF",
        "head": "beluga",
        "tail": "bolt",
    }


@app.post("/start")
def handle_start():
    global snake

    data = request.get_json()
    snake = Snake(data)

    return "ok"


@app.post("/move")
def handle_move():
    global snake

    data = request.get_json()
    snake.set_data(data)
    move = snake.choose_move()

    return {"move": move}


@app.post("/end")
def end():
    global snake

    data = request.get_json()
    snake.set_data(data)

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
