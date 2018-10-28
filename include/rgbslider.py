
from include.rect import Rect
from include.slider import Slider

class RGBSlider:
    def __init__(self, RSLIDER, GSLIDER, BSLIDER, window, label, varset, id_):
        self.RSLIDER = RSLIDER
        self.GSLIDER = GSLIDER
        self.BSLIDER = BSLIDER
        self.sliders = RSLIDER, GSLIDER, BSLIDER
        self.window = window
        self.label = label
        self.varset = varset
        self.id_ = id_
        for slider in self.sliders:
            if not isinstance(slider, Slider):
                raise TypeError(f"RGBSlider class initialised with non slider type  slider: {type(slider)}")
        if not isinstance(window, Rect):
            raise TypeError(f"RGBSlider class initialised with non Rect type window: {type(window)}")

    def __repr__(self):
        return f"""
{self.label.text}
RGBSLIDER:
    RED{self.RSLIDER}
    GREEN{self.GSLIDER}
    BLUE{self.BSLIDER}
    current rgb value: {self.get_color()}
    varset: {self.varset}
/{self.label.text}
"""

    def set_value(self, color):
        r, g, b = color
        self.RSLIDER.set_value(r)
        self.GSLIDER.set_value(g)
        self.BSLIDER.set_value(b)

    def draw(self):
        self.label.draw()
        [slider.draw() for slider in self.sliders]
        self.window.color = self.window.check_color(self.get_color())
        self.window.draw()

    def get_color(self):
        r = self.RSLIDER.get_value()
        g = self.GSLIDER.get_value()
        b = self.BSLIDER.get_value()
        return (r,g,b)

    def set_var(self):
        self.varset = self.get_color()
