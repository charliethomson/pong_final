
from pyglet.text import Label
from include.rect import *
from include.vector2d import Vector2D

class MenuButton:
    def __init__(self, x, y, w, h, text, function, color=WHITE, multiline=False, function_args=None):
        self.text = text
        self.pos = Vector2D(x, y)
        self.w, self.h = w, h
        if function_args:
            self.function_args = function_args if isinstance(function_args, (list, tuple)) else [function_args,]
        else: self.function_args = None
        self.function = function
        self.color = color
        self.multiline = multiline
        self.COLOR = color

    def __repr__(self):
        ## DEBUG ##
        return f"BUTTON DATA: \n\ttext: {self.text} \n\tpos: {self.pos} \n\tw: {self.w} \n\th: {self.h} \n\tfunction: {self.function.__name__} \n\tcolor: {self.color}\n"

    def draw(self):
        # print("DRAWING")
        Rect(self.pos.x, self.pos.y, self.w, self.h, color=self.color, draw=True)
        self.label = Label(
            text=self.text,
            x=self.pos.x,
            y=self.pos.y,
            anchor_x=CENTER,
            # anchor_y=CENTER,
            width=self.w,
            height=-self.h,
            font_size=25,
            font_name="helvetica"
        )
        self.label.draw()
        self.color = self.COLOR

    def contains(self, point: Vector2D) -> bool:
        if not isinstance(point, Vector2D):
            raise TypeError(f"point incorrect type; expected {type(Vector2D)} recieved {type(point)}")

        return (
                point.x < self.pos.x + self.w // 2
            and point.x > self.pos.x - self.w // 2
            and point.y < self.pos.y + self.h // 2
            and point.y > self.pos.y - self.h // 2
            )

    def on_hover(self):
        # print(self.label.text)
        self.color = tuple([color + 25 for color in self.color])

    def on_click(self):
        if not self.function_args:  
            self.function()
        else:

            self.function(*self.function_args)
