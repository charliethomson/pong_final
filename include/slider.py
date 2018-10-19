
from include.rect import *
from include.remap import remap
from include.vector2d import Vector2D

from pyglet.text import Label

class Slider:
    def __init__(self, x, y, w, h, min_, max_, color, id_, title=None):
        self.curpos = Vector2D(x, y)
        self.rectpos = Vector2D(x, y)
        self.w, self.h = w, h
        self.range_ = self.min_, self.max_ = min_, max_
        self.color = color
        self.id_ = id_
        self.title = title
        self.minx, self.maxx = self.rectpos.x - self.w // 2 + self.h // 2, self.rectpos.x + self.w // 2 - self.h // 2

    def __repr__(self):
        return (f"""
SLIDER DATA:
    current position: {self.curpos}
    rectangle position: {self.rectpos}
    width: {self.w}
    height: {self.h}
    range (given min, max): {self.range_}
    min x: {self.minx}
    max x: {self.maxx}
    color: {self.color}
    current value: {self.get_value()}
    title: {self.title}
        """)

    def draw(self):
        if self.title:
            Label(
                text=self.title,
                x=self.rectpos.x,
                y=self.rectpos.y + self.h
            ).draw()

        Rect(self.rectpos.x, self.rectpos.y, self.w, self.h, color=self.color, draw=True)
        Rect(self.curpos.x, self.curpos.y, self.h - 2, self.h - 2, color=tuple([color + 25 for color in self.color]))
        Label(
            text=str(self.get_value()),
            x=self.curpos.x,
            y=self.curpos.y,
            anchor_x=CENTER,
            anchor_y="baseline",
            width=self.h,
            height=self.h
        ).draw()

    def contains(self, point):
        if not isinstance(point, Vector2D): raise TypeError("point must me Vector2D")
        return (
                point.x < self.curpos.x + self.h // 2
            and point.x > self.curpos.x - self.h // 2
            and point.y < self.curpos.y + self.h // 2
            and point.y > self.curpos.y - self.h // 2
            )



    def get_value(self):
        return int(remap(self.curpos.x, self.minx, self.maxx, self.min_, self.max_))
