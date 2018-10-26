
from include.slider import Slider
from include.button import MenuButton
from include.vector2d import Vector2D
from include.rgbslider import RGBSlider

class Menu:
    def __init__(self):
        self.buttons = []
        self.sliders = []
        self.rgbsliders = []
        self.elements = [self.buttons, self.sliders, self.rgbsliders]

    def __repr__(self):
        return "\n############################\nButtons: \n" +\
                str([button for button in self.buttons]) +\
                "\n###########################\nSliders: \n" +\
                str([slider for slider in self.sliders]) +\
                "\n###########################\nRGBSliders: \n" +\
                str([rgbslider for rgbslider in self.rgbsliders]) +\
                "\n###########################\n\n"

    def add_button(self, button):
        if not isinstance(button, MenuButton):
            raise TypeError("cannot add non button item to menu (<Menu>.add_button())")
        self.buttons.append(button)

    def add_slider(self, slider):
        if not isinstance(slider, Slider):
            raise TypeError("cannot add non slider item to menu (<Menu>.add_slider())")
        self.sliders.append(slider)

    def add_rgbslider(self, rgbslider):
        if not isinstance(rgbslider, RGBSlider):
            raise TypeError("cannot add non rbgslider item to menu (<Menu>.add_rgbslider())")
        self.rgbsliders.append(rgbslider)

    def get_element_by_id(self, id_, type_=None):
        """
        if no type given, returns the first item found in buttons (or) -> sliders (or) -> rgbsliders with the id `id_`
        if a type is given, returns the first item of type `type_` with id `id_`
        """
        types = {
            "button": self.buttons,
            "slider": self.sliders,
            "rgbslider": self.rgbsliders
        }
        if type_:
            for item in types[type_]:
                if item.id_ == id_:
                    return item
        else:
            for element_type in self.elements:
                for item in element_type:
                    if item.id_ == id_:
                        return item
        
            

        raise Exception(f"item with id {id_} not found (<Menu>.get_element_by_id)")


    def mouse_pressed(self, x, y, button, mod):
        for button in self.buttons:
            if button.contains(Vector2D(x, y)):
                button.on_click()

        for slider in self.sliders:
            if slider.back_contains(Vector2D(x, y)) and slider.minx < x < slider.maxx:
                slider.curpos.x = x

        for rgbslider in self.rgbsliders:
            for slider in rgbslider.sliders:
                if slider.back_contains(Vector2D(x, y)) and slider.minx < x < slider.maxx:
                    slider.curpos.x = x
            
        


    def mouse_drag(self, x, y, dx, dy, button, mod):
        for slider in self.sliders:
            if slider.contains(Vector2D(x, y)) and slider.minx < x < slider.maxx:
                slider.curpos.x = x
        for rgbslider in self.rgbsliders:
            for slider in rgbslider.sliders:
                if slider.contains(Vector2D(x, y)) and slider.minx < x < slider.maxx:
                    slider.curpos.x = x


    def draw(self):
        # print("Drawing")
        [button.draw() for button in self.buttons]
        [slider.draw() for slider in self.sliders]
        [rgbslider.draw() for rgbslider in self.rgbsliders]
