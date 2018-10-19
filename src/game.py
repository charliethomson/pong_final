from src.puck import Puck
from src.menu import Menu
from src.paddle import Paddle

from include.rect import *
from include.slider import Slider
from include.button import MenuButton
from include.options import Options
from include.vector2d import Vector2D
from include.rgbslider import RGBSlider
from include.frame_counter import FrameCounter

from pyglet.text import Label
from pyglet.window.key import W, S, UP, DOWN, P

from os import listdir
from time import strftime
from yaml import load as load_yaml
from yaml import dump as dump_yaml
from pprint import pprint


class Game:
    def __init__(self, window, keys):
        self.window = window
        self.keys = keys
        self.frame_counter = FrameCounter(0)
        self.mouse_position = Vector2D()
        self.player1 = Paddle(self.window, self.keys, 0)
        self.player2 = Paddle(self.window, self.keys, 1)
        self.players = self.player1, self.player2
        self.puck = Puck(self.window)
        self.is_running = False
        self.is_paused = False
        self.visible_menu = "main_menu"
        self.last_menu = None
        self.menus = {}
        self.varsets = {
            "P1COLOR": self.player1.color,
            "P2COLOR": self.player2.color,
            "PUCKCOLOR": self.puck.color
        }
        self.functions = {
            "start_game": self.start_game,
            "goto_loadmenu": self.goto_loadmenu,
            "goto_options": self.goto_options,
            "exit_game": self.exit_game,
            "toggle_fullscreen": self.toggle_fullscreen,
            "goto_mainmenu": self.goto_mainmenu,
            "save_game": self.save_game,
            "pause_game": self.pause_game,
            "unpause_game": self.unpause_game,
            "go_back": self.go_back,
            ###
            "load_game": self.load_game
        }
        self.load_menus()
        self.print_menu_data()

    def apply_options(self):        
        options_menu = self.menus["options"]
        self.options.set_fullscreen(self.window.fullscreen)
        self.options.set_difficulty(options_menu.get_element_by_id("difficulty", "slider").get_value())
        self.options.set_puck_color(options_menu.get_element_by_id("puck_color", "rgbslider").get_color())
        self.options.set_player1_color(options_menu.get_element_by_id("player1_color", "rgbslider").get_color())
        self.options.set_player2_color(options_menu.get_element_by_id("player2_color", "rgbslider").get_color())
        self.options.apply_options(self)

    def print_menu_data(self):
        for filename in listdir("./menus"):
            with open("./menus/" + filename, "r") as file_:
                if "load" in filename: continue
                yaml_data = load_yaml(file_)["menu"]
                print("\nYaml data for file %s" % filename)
                pprint(yaml_data)


    def reset(self):
        self.puck.reset()
        for player in self.players:
            player.reset()
            player.score = 0

    def mouse_pressed(self, x, y, button, mod):
        if self.visible_menu:
            menu = self.menus[self.visible_menu]
            menu.mouse_pressed(x, y, button, mod)

    def mouse_drag(self, x, y, dx, dy, button, mod):
        if self.visible_menu:
            menu = self.menus[self.visible_menu]
            menu.mouse_drag(x, y, dx, dy, button, mod)

    def start_game(self):
        self.is_paused = False
        self.is_running = True
        self.last_menu = self.visible_menu
        self.visible_menu = None
        self.reset()

    def save_game(self):
        filename = "./saves/" + strftime("%d%m%Y-%H_%M_%S") + ".yaml"
        save_data = {
                "puck":
                    {"pos": self.puck.pos,
                     "vel": self.puck.vel,
                     "color": self.puck.color},
                "player1":
                    {"pos": self.player1.pos,
                    "score": self.player1.score,
                    "color": self.player1.color},
                "player2":
                    {"pos": self.player2.pos,
                    "score": self.player2.score,
                    "color": self.player2.color}
            }
        with open(filename, "w") as file_:
            file_.write(dump_yaml(save_data))
        
        with open("./menus/load_menu.yaml", "r+") as load_menu_file:
            existing_yaml_data = load_yaml(load_menu_file.read())
            yaml_data = existing_yaml_data["menu"]
            pages = yaml_data["pages"]
            pprint(existing_yaml_data)
            pprint(pages)
            top_value, page_number = None, None

            # if it's empty, put the data at the first place on the first page
            if not pages:
                page_number = 1
                top_value = 1

            else:
                for key in pages.keys():
                    if len(pages[key]) < 5:
                        page_number = key
                        for value in pages[key]:
                            top_value = value + 1
            
            # if there's no page with an open slot, put it at the first spot on the next page
            if not top_value and not page_number:
                page_number = max([key for key in pages.keys()]) + 1
                top_value = 1
            
            print(page_number, top_value)
            

    def load_game(self, filename="test.yaml"):
        if not filename.split('.')[1] == "yaml":
            raise ImportError(f"filename extension incorrect {filename.split('.')[1]}")
        
        def remove_duplicates(a, b):
            """
            removes all items that are in a from b and returns b
            a = [1, 2, 3, 4]
            b = [3, 4, 5, 6]
            c = remove_duplicates(a, b)
            c = 5, 6
            """
            if not isinstance(a, list) and not isinstance(b, list):
                raise TypeError("a and b must be lists")
            
            for item in a:
                if item in b:
                    b.remove(item)
            
            return b

        with open("./saves/" + filename) as file_:
            yaml_data = load_yaml(file_.read())
            missing = ""
            acceptable = ["player1", "player2", "puck"]
            datapoints = [data for data in yaml_data]
            missing_datapoints = remove_duplicates(datapoints, acceptable)
            missing += ', '.join(missing_datapoints)
            if missing != '':
                raise ImportError(f"error importing save from file {filename}; \nmissing data point{'' if ',' not in list(missing) else 's'} {missing}")
            player1 = yaml_data["player1"]
            player2 = yaml_data["player2"]
            puck = yaml_data["puck"]
            
            self.player1.pos = player1["pos"]
            self.player1.color = player1["color"]
            self.player1.score = player1["score"]

            self.player2.pos = player2["pos"]
            self.player2.color = player2["color"]
            self.player2.score = player2["score"]

            self.puck.pos = puck["pos"]
            self.puck.vel = puck["vel"]
            self.puck.color = puck["color"]
        self.start_game()

    def go_back(self):
        if self.visible_menu == "options": self.apply_options()
        self.visible_menu = self.last_menu

    def goto_mainmenu(self):
        self.is_paused = False
        self.is_running = False
        self.last_menu = self.visible_menu
        self.visible_menu = "main_menu"

    def goto_loadmenu(self):
        self.reset()

    def goto_options(self):
        self.is_paused = False
        self.last_menu = self.visible_menu
        self.visible_menu = "options"
    
    def unpause_game(self):
        self.is_running = True
        self.is_paused = False
        self.last_menu = self.visible_menu
        self.visible_menu = None

    def pause_game(self):
        self.is_running = False
        self.is_paused = True
        self.last_menu = self.visible_menu
        self.visible_menu = "pause"

    def toggle_fullscreen(self):
        file = open("./resources/temp.yaml", "w+"); file.close()
        self.puck._temp_save_pos()
        for player in self.players:
            player._temp_save_pos()

        self.window.set_fullscreen(not self.window.fullscreen)
        self.load_menus()

        self.puck._load_pos_from_temp()
        for player in self.players:
            player._load_pos_from_temp()
        file = open("./resources/temp.yaml", "w+"); file.close()

    def exit_game(self):
        print("Exiting")
        self.window.close()
        exit()

    def mainloop(self, dt):
        self.frame_counter.on_frame()
        self.window.clear()
        if self.is_running:
            if self.keys[P]: self.pause_game()
            self.handle_motion()
            self.handle_collision()
            self.keep_in_bounds()
            self.puck.draw()
            self.puck.update()
            self.draw_scores()
            [player.draw() for player in self.players]
        else:
            if self.visible_menu:
                # print(self.visible_menu)
                menu = self.menus[self.visible_menu]
                menu.draw()
                for button in menu.buttons:
                    if button.contains(self.mouse_position):
                        button.on_hover()
        if self.is_paused:
            # if self.keys[P]: self.unpause_game()
            self.puck.draw()
            self.draw_scores()
            [player.draw() for player in self.players]
        if self.visible_menu == "pause": self.is_paused = True
        else: self.is_paused = False


    def handle_motion(self):
        if self.keys[W]:    self.player1.move( 10)
        if self.keys[S]:    self.player1.move(-10)
        if self.keys[UP]:   self.player2.move( 10)
        if self.keys[DOWN]: self.player2.move(-10)

    def handle_collision(self):
        for player in self.players:
            # i wrote this collision algorithm legit like 4 months ago and I don't remember how so I keep reusing it lmao
            if (
                (
                 self.puck.pos.y - self.puck.h // 2 > player.pos.y - player.h // 2 and
                 self.puck.pos.y + self.puck.h // 2 < player.pos.y + player.h // 2
                ) and not
                 (self.puck.pos.x + self.puck.w // 2 < player.pos.x - player.w // 2 or
                  self.puck.pos.x - self.puck.w // 2 > player.pos.x + player.w // 2
                 )
                ):
                self.puck.vel.x *= -1

    def keep_in_bounds(self):
        for player in self.players:
            # if it goes too low, reset it to the lowest it'll go
            if player.pos.y < player.h // 2:
                player.pos.y = player.h // 2
            # if it goes too high, reset it to the highest it'll go
            if player.pos.y > self.window.height - player.h // 2:
                player.pos.y = self.window.height - player.h // 2
        # make the puck bounce if it hits the roof or floor
        if (self.puck.pos.y < self.puck.h // 2
         or self.puck.pos.y > self.window.height - self.puck.h // 2):
            self.puck.vel.y *= -1
        # if it goes off to the left, increment player2's score and reset the puck
        if self.puck.pos.x < 0:
            self.reset()
            self.player2.score += 1
        # if it goes off to the right, increment player1's score and reset the puck
        if self.puck.pos.x > self.window.width:
            self.reset()
            self.player1.score += 1

    def draw_scores(self):
        # player1 score
        Label(
            text=str(self.player1.score),
            x=4,
            y=self.window.height - 40,
            font_name="helvetica",
            font_size=36
        ).draw()
        # var to store the position the label needs to be drawn at
        # stays accurate enough till like 100000 ish
        LABEL_X_POS = self.window.width - len(list(str(self.player2.score))) * 30
        # player2 score
        Label(
            text=str(self.player2.score),
            x=LABEL_X_POS,
            y=self.window.height - 40,
            font_name="helvetica",
            font_size=36
        ).draw()

    def load_menus(self):
        def get_slider_data(slider):
            x, y = slider["x"] * self.window.width, slider["y"] * self.window.height
            w, h = slider["w"] * self.window.width, slider["h"] * self.window.height
            min_, max_ = slider["min"], slider["max"]
            id_ = slider["id"]
            color = [int(num) for num in slider["color"].split(",")]
            return (x, y, w, h, min_, max_, color, id_)

        def get_button_data(button):
            x, y = button["x"] * self.window.width, button["y"] * self.window.height
            w, h = button["w"] * self.window.width, button["h"] * self.window.height
            text = button["text"]
            id_ = button["id"]
            function = self.functions[button["function"]]
            color = [int(num) for num in button["color"].split(",")]
            return (x, y, w, h, text, function, id_, color)

        for filename in listdir("./menus"):
            with open("./menus/" + filename, "r") as file_:
                if "load" in filename: continue
                yaml_data = load_yaml(file_)["menu"]
                menu_name = yaml_data["name"]
                menu = Menu()
                buttons = None 
                sliders = None
                rgbsliders = None

                if "buttons" in yaml_data.keys():
                    buttons = yaml_data["buttons"]
                if "sliders" in yaml_data.keys():
                    sliders = yaml_data["sliders"]
                if "rgbsliders" in yaml_data.keys():
                    rgbsliders = yaml_data["rgbsliders"]

                if buttons:
                    for key in buttons.keys():
                        button = buttons[key]
                        data = get_button_data(button)
                        multiline = button["multiline"] if "multiline" in buttons.keys() else False
                        menu.add_button(MenuButton(*data, multiline=multiline))

                if sliders:
                    for key in sliders.keys():
                        slider = sliders[key]
                        data = get_slider_data(slider)
                        menu.add_slider(Slider(*data))

                if rgbsliders:
                    for key in rgbsliders.keys():
                        rgbslider = rgbsliders[key]
                        varset = self.varsets[rgbslider["VARSET"]]
                        RSLIDER = Slider(*get_slider_data(rgbslider["R"]))
                        GSLIDER = Slider(*get_slider_data(rgbslider["G"]))
                        BSLIDER = Slider(*get_slider_data(rgbslider["B"]))
                        id_ = rgbslider["id"]
                        win = rgbslider["window"]
                        window = Rect(
                            win["x"] * self.window.width,
                            win["y"] * self.window.height,
                            win["w"] * self.window.height,
                            win["h"] * self.window.height
                        )
                        LABEL = rgbslider["label"]
                        label = Label(
                            text=LABEL["text"],
                            x=LABEL["x"] * self.window.width,
                            y=LABEL["y"] * self.window.height,
                            anchor_x="center"
                        )
                        menu.add_rgbslider(RGBSlider(RSLIDER, GSLIDER, BSLIDER, window, label, varset, id_))


                self.menus[menu_name] = menu

    def build_load_menus(self):
        pass








































#
