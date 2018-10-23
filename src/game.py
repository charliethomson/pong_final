from src import load_menu_ratios

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
from pyglet.window import FPSDisplay

from os import listdir
from os import remove as rm
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
        self.options = Options()
        self.is_running = False
        self.show_fps = True
        self.is_paused = False
        self.visible_menu = "main_menu"
        self.current_page = 0
        self.last_menu = None
        self.fps_clock = FPSDisplay(self.window)
        self.menus = {}
        self.load_menu_pages = {}
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
            "toggle_show_fps": self.toggle_show_fps,
            "goto_mainmenu": self.goto_mainmenu,
            "save_game": self.save_game,
            "pause_game": self.pause_game,
            "unpause_game": self.unpause_game,
            "go_back": self.go_back,
            "delete": self.delete_save,
            "load_game": self.load_game
        }
        self.load_menus()
        # self.print_menu_data()

    def apply_options(self):        
        options_menu = self.menus["options"]
        new_difficulty = options_menu.get_element_by_id("difficulty", "slider").get_value()
        if new_difficulty != self.puck.magnitude: self.reset()
        self.options.set_fullscreen(self.window.fullscreen)
        self.options.set_difficulty(new_difficulty)
        self.options.set_puck_color(options_menu.get_element_by_id("puck_color", "rgbslider").get_color())
        self.options.set_player1_color(options_menu.get_element_by_id("player1_color", "rgbslider").get_color())
        self.options.set_player2_color(options_menu.get_element_by_id("player2_color", "rgbslider").get_color())
        self.options.apply_settings(self)

    def print_menu_data(self):
        for filename in listdir("./menus"):
            with open("./menus/" + filename, "r") as file_:
                if "load" in filename: continue
                yaml_data = load_yaml(file_)["menu"]
                print("\nYaml data for file %s" % filename)
                pprint(yaml_data)


    def full_reset(self):
        self.puck.reset()
        for player in self.players:
            player.reset()
            player.score = 0

    def toggle_show_fps(self):
        self.show_fps = not self.show_fps

    def reset(self):
        self.puck.reset()
        [player.reset() for player in self.players]

    def mouse_pressed(self, x, y, button, mod):
        if self.visible_menu:
            if not self.visible_menu == "load_menu":
                menu = self.menus[self.visible_menu]
                menu.mouse_pressed(x, y, button, mod)
            else:
                page = self.load_menu_pages[self.current_page]
                page.mouse_pressed(x, y, button, mod)

    def mouse_drag(self, x, y, dx, dy, button, mod):
        if self.visible_menu:
            if self.visible_menu == "load_menu": return 0;
            menu = self.menus[self.visible_menu]
            menu.mouse_drag(x, y, dx, dy, button, mod)

    def start_game(self):
        self.is_paused = False
        self.is_running = True
        self.last_menu = self.visible_menu
        self.visible_menu = None
        self.full_reset()

    def save_game(self):
        filename = "./saves/" + strftime("%d%m%y-%H_%M_%S") + ".yaml"
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
        
        self.unpause_game()

    def go_back(self):
        if self.visible_menu == "options": self.apply_options()
        self.visible_menu = self.last_menu

    def goto_mainmenu(self):
        self.is_paused = False
        self.is_running = False
        self.last_menu = self.visible_menu
        self.visible_menu = "main_menu"

    def goto_loadmenu(self):
        if len(listdir("./saves")) == 0: print("No saves"); return 0
        print("Building menu")
        self.build_load_menus()
        print("Finished")
        if not self.last_menu == self.visible_menu:
            self.last_menu = self.visible_menu
        self.visible_menu = "load_menu"

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
        if self.show_fps:
            self.fps_clock.draw()
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
                if self.visible_menu == "load_menu":
                    # print(self.load_menu_pages)
                    page = self.load_menu_pages[self.current_page]
                    page.draw()
                    for button in page.buttons:
                        if button.contains(self.mouse_position):
                            button.on_hover()
                else:
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


        TOTAL_PAGES = (len(listdir("./saves")) / 5)
        print(TOTAL_PAGES)
        # if it's not a whole number
        if TOTAL_PAGES % 1 != 0.0:
            TOTAL_PAGES = int(TOTAL_PAGES) + 1
            EVEN_PAGES = False
        else:
            TOTAL_PAGES = int(TOTAL_PAGES)
            EVEN_PAGES = True
        print(TOTAL_PAGES)
        page = Menu()

        def commit_page(page, page_number):
            if page_number != 0:
                # last page button
                print("i", page_number)
                page.add_button(MenuButton(0.315 * self.window.width, 
                                           0.14 * self.window.height, 
                                           h,
                                           h,
                                           "<",
                                           self.goto_load_menu_page, 
                                           color=MID_GRAY, 
                                           id_="load_last_page", 
                                           function_args=page_number - 1)
                )
                
            # back button
            page.add_button(MenuButton(0.500 * self.window.width,
                                       0.140 * self.window.height,
                                       w,
                                       h,
                                       "Back",
                                       self.go_back,
                                       color=MID_GRAY,
                                       id_="load_go_back")
            )


            if page_number != TOTAL_PAGES - 1:
                # next page button
                print("AAAA", page_number, TOTAL_PAGES)
                page.add_button(MenuButton(0.685 * self.window.width,
                                           0.140 * self.window.height,
                                           h, 
                                           h,
                                           ">",
                                           self.goto_load_menu_page,
                                           color=MID_GRAY,
                                           id_="load_next_page",
                                           function_args=page_number + 1)

                )

            self.load_menu_pages[page_number] = page

        for index, save in sorted(enumerate(listdir("./saves"))):
            
            page_number = index // 5
            x = 0.50 * self.window.width
            y = load_menu_ratios[index % 5] * self.window.height
            w = 0.25 * self.window.width
            h = 0.10 * self.window.height

            del_x = 0.685 * self.window.width


            page.add_button(MenuButton(del_x, y, h, h, "x", self.delete_save, color=MID_GRAY, id_=f"delete game - {save}", function_args=save))
            page.add_button(MenuButton(x, y, w, h, save.split('.')[0], self.load_game, color=MID_GRAY, id_=f"load_game - {save}", function_args=save))
            if len(page.buttons) == 10:
                commit_page(page, page_number)
                page = Menu()
        # try:
        #     page.get_element_by_id("load_go_back")
        # except Exception:
        #     commit_page(page, page_number)
        # print(page)
        if not EVEN_PAGES:

            commit_page(page, page_number)
            print(self.load_menu_pages.keys())

    def delete_save(self, filename):
        rm("./saves/" + filename)
        self.build_load_menus()

        if self.load_menu_pages[self.current_page].buttons

    def goto_load_menu_page(self, page_number):
        if page_number == -1: self.go_back()
        if not page_number in self.load_menu_pages.keys(): raise ValueError("page_number incorrect")
        print("current: ", page_number)
        self.current_page = page_number

            




#
