
from include.rect import *
from include.vector2d import Vector2D

from yaml import dump as dump_yaml, load as load_yaml

class Paddle:
    def __init__(self, window, keys, side):
        self.window = window
        self.keys = keys
        self.side = side
        self.w, self.h = self.window.width // 40, self.window.height // 3.5
        self.reset()
        self.color = (127, 127, 127)
        self.score = 0

    def draw(self):
        Rect(self.pos.x, self.pos.y, self.w, self.h, color=self.color)

    def reset(self):
        x = self.w + 10 if not self.side else self.window.width - self.w - 10
        self.pos = Vector2D(x, self.window.height // 2)

    def move(self, amount):
        self.pos.y += amount
