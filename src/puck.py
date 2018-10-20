from math import sin, cos, pi
from random import random
from yaml import dump, load

from include.rect import *
from include.vector2d import Vector2D

class Puck:
    def __init__(self, window):
        self.window = window
        self.magnitude = 10
        self.w, self.h = 25, 25
        self.color = (127, 127, 127)
        self.reset()

    def reset(self):
        self.pos = Vector2D(self.window.width // 2, self.window.height // 2)
        angle = (random() * 2 * pi) - pi
        self.vel = Vector2D(self.magnitude * sin(angle), self.magnitude * cos(angle))

    def _temp_save_pos(self):
        with open("./resources/temp.yaml", "a+") as file_:
            file_.write(dump(
                {"puck": (self.pos.x / self.window.width, self.pos.y / self.window.height)}
                )
            )
    
    def _load_pos_from_temp(self):
        with open("./resources/temp.yaml", "r") as file_:
            yaml_data = load(file_.read())
            data = yaml_data["puck"]
            self.pos.x = data[0] * self.window.width
            self.pos.y = data[1] * self.window.height

    def draw(self):
        Rect(self.pos.x, self.pos.y, self.w, self.h, color=self.color)

    def update(self):
        self.pos += self.vel
