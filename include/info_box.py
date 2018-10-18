
from include.rect import *
from include.vector2d import Vector2D

from pyglet.text import Label

class InfoBox:
    def __init__(self, text, w, h):
        self.pos = Vector2D()
        self.w, self.h = w, h
        self.text = text

    def draw(self):
        Rect(self.pos.x, self.pos.y - self.h, self.w, self.h, color=(55, 55, 55), mode=CORNER)
        Label(
            text=self.text,
            x=self.pos.x,
            y=self.pos.y,
            width=self.w,
            height=self.h,
            anchor_x="left",
            anchor_y="baseline",
            font_size=15,
            font_name="helvetica",
            multiline=True
        ).draw()
