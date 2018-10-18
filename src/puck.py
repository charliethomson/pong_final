from math import sin, cos, pi
from random import random

from include.rect import *
from include.vector2d import Vector2D

class Puck:
    def __init__(self, window):
        self.window = window
        self.magnitude = 10
        self.w, self.h = 25, 25
        self.color = WHITE
        self.reset()

    def reset(self):
        self.pos = Vector2D(self.window.width // 2, self.window.height // 2)
        angle = (random() * 2 * pi) - pi
        self.vel = Vector2D(self.magnitude * sin(angle), self.magnitude * cos(angle))

    def draw(self):
        Rect(self.pos.x, self.pos.y, self.w, self.h, color=self.color)

    def update(self):
        self.pos += self.vel
