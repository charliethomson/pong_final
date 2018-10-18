
from include.rect import *
from include.vector2d import Vector2D

from yaml import dump, load

class Paddle:
    def __init__(self, window, keys, side):
        self.window = window
        self.keys = keys
        self.side = side
        self.w, self.h = self.window.width // 40, self.window.height // 3.5
        self.reset()
        self.color = WHITE
        self.score = 0

    def draw(self):
        Rect(self.pos.x, self.pos.y, self.w, self.h, color=self.color)

    def _temp_save_pos(self):
        with open("./resources/temp.yaml", "a+") as file_:
            # player 1
            if not self.side:
                # dump yaml
                file_.write(dump(
                        {"player1": (self.pos.x / self.window.width, self.pos.y / self.window.height)}
                    )
                )
            # player 2
            else:
                # dump yaml
                file_.write(dump(
                        {"player2": (self.pos.x / self.window.width, self.pos.y / self.window.height)}
                    )
                )
    
    def _load_pos_from_temp(self):
        with open("./resources/temp.yaml", "r") as file_:
            yaml_data = load(file_.read())
            # player 1
            if not self.side:
                data = yaml_data["player1"]
            else:
                data = yaml_data["player2"]
            
            self.pos.x = data[0] * self.window.width
            self.pos.y = data[1] * self.window.height



    def reset(self):
        x = self.w + 10 if not self.side else self.window.width - self.w - 10
        self.pos = Vector2D(x, self.window.height // 2)

    def move(self, amount):
        self.pos.y += amount
