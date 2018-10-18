
from pyglet.gl import GL_QUADS
from pyglet.graphics import draw as gl_draw

# MODE CONSTANTS
CENTER = "center"
CORNER = "corner"
CORNERS = "corners"
#

# COLOR CONSTANTS
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
BLACK = (  0,   0,   0)
#

class Rect:
    def __init__(self, x, y, w, h, color=(255, 255, 255), mode=CENTER, draw=True):
        self.x, self.y, self.w, self.h = int(x), int(y), int(w), int(h)
        self.color = self.check_color(color)
        self.mode = mode


        self.coords = [                                 # if the mode is center
            self.x - self.w // 2, self.y + self.h // 2, # top left
            self.x + self.w // 2, self.y + self.h // 2, # top right
            self.x + self.w // 2, self.y - self.h // 2, # bottom right
            self.x - self.w // 2, self.y - self.h // 2  # bottom left
        ] if self.mode == CENTER else [             # if the mode is corner
            self.x         , self.y + self.h,       # top left
            self.x + self.w, self.y + self.h,       # top right
            self.x + self.w, self.y         ,       # bottom right
            self.x         , self.y                 # bottom left
        ] if self.mode == CORNER else [ # if the mode is corners
            self.x, self.h,             # top left
            self.w, self.h,             # top right
            self.w, self.y,             # bottom right
            self.x, self.y              # bottom left
        ] if self.mode == CORNERS else None

        if not self.coords: raise ValueError("mode incorrect")

        if draw:
            self.draw()

    def check_color(self, color):
        ret_color = color * 4 if len(color) == 3 else (color, color) * 6 if isinstance(color, int) else color if len(color) == 12 else None
        if not ret_color: raise ValueError("Data for color incorrect length")
        return ret_color

    def draw(self):
        gl_draw(4, GL_QUADS,
                ("v2i", self.coords),
                ("c3B", self.color)
               )
