from . import load_menu_ratios

from .puck import Puck
from .menu import Menu
from .paddle import Paddle


from include.rect import *
from include.slider import Slider
from include.button import MenuButton
from include.options import Options
from include.vector2d import Vector2D
from include.rgbslider import RGBSlider

from pyglet.text import Label
from pyglet.image import load
from pyglet.window import FPSDisplay
from pyglet.window.key import W, S, UP, DOWN, P, LCTRL, LALT, D

from os import listdir
from os import remove as rm
from sys import exit as sysexit
from time import strftime
from yaml import load as load_yaml
from yaml import dump as dump_yaml
from pprint import pprint


class Game:
    def __init__(self, window, keys):
        """
        window: the window for the game to be run in
        keys: <pyglet.window.key.KeyStateHandler> object that handles keys
        """
        self.window = window

        self.keys = keys
        self.mouse_position = Vector2D()

        self.options = Options()
        self.show_fps = True
        self.fps_clock = FPSDisplay(self.window)

        self.player1 = Paddle(self.window, self.keys, 0)
        self.player2 = Paddle(self.window, self.keys, 1)
        self.players = self.player1, self.player2

        self.puck = Puck(self.window)

        self.is_paused = False
        self.is_running = False

        self.menus = {}
        self.last_menu = None
        self.visible_menu = "main_menu"
        self.current_save = None

        self.current_page = 0
        self.load_menu_pages = {}

        self.varsets = {
            "P1COLOR": self.player1.color,
            "P2COLOR": self.player2.color,
            "PUCKCOLOR": self.puck.color
        }
        self.functions = {
            "toggle_fullscreen": self.toggle_fullscreen,
            "toggle_show_fps": self.toggle_show_fps,
            "goto_mainmenu": self.goto_mainmenu,
            "goto_loadmenu": self.goto_loadmenu,
            "goto_options": self.goto_options,
            "unpause_game": self.unpause_game,
            "reset_game": self.full_reset,
            "start_game": self.start_game,
            "pause_game": self.pause_game,
            "load_game": self.load_game,
            "save_game": self.save_game,
            "exit_game": self.exit_game,
            "delete": self.delete_save,
            "go_back": self.go_back
        }

        self.load_menus()

    def _cleanup(self):
        """
        clear some files before closing, so no temp data carries over from one game instance to another
        """
        open("./resources/.temp_options.yaml", "w+").close()
        open("./resources/.temp.yaml", "w+").close()

    def _init_temp_options(self):
        """
        Preps the file that stores unsaved options for writing
        """
        with open("./resources/.temp_options.yaml", "w") as file_:
            file_.write(
                dump_yaml(
                        {
                    "options": Options()
                    }
                )
            )

    def _print_menu_data(self):
        """
        pprints the data for all the menus
        """
        for filename in listdir("./menus"):
            with open("./menus/" + filename, "r") as file_:
                if "load" in filename: continue
                yaml_data = load_yaml(file_)["menu"]
                print("\nYaml data for file %s" % filename)
                pprint(yaml_data)

    def setup(self):

        favicon = load("./resources/favicon.png")
        self.window.set_icon(favicon)
        self.window.set_caption("Pong v1.4")
        self._init_temp_options()
        self.full_reset()

        
    def apply_options(self):
        """
        Applies options from either the save or the temp game options file
        """
        options_menu = self.menus["options"]
        # Sets the options variable to a new Options instance
        self.options = Options(
            player1_color = options_menu.get_element_by_id("player1_color").get_color(),
            player2_color = options_menu.get_element_by_id("player2_color").get_color(),
            puck_color    = options_menu.get_element_by_id("puck_color"   ).get_color(),
            difficulty    = options_menu.get_element_by_id("difficulty", "slider").get_value(),
            is_fullscreen = self.window.fullscreen
        )
        # Applies the new options
        self.options.apply_settings(self)
        with open("./resources/.temp_options.yaml", "w") as file_:
            # Writes the new options to the temp file
            file_.write(dump_yaml({"options": self.options}))

    def full_reset(self):
        """
        resets the game entirely (scores and positions)
        """
        self.puck.reset()
        for player in self.players:
            player.reset()
            player.score = 0
        if self.is_paused:
            self.unpause_game()

    def toggle_show_fps(self, set_=None):
        """
        switches on/of the fps display
        """
        # if no set is given, it toggles
        if set_ == None:
            self.show_fps = not self.show_fps
        # otherwise, if it's a bool or int (True, False; 1, 0), it sets it to the given value
        else:
            assert isinstance(set_, (bool, int)), "set_ must be bool or int"
            self.show_fps = set_

    def reset(self):
        """
        resets the puck, players' positions
        """
        self.puck.reset()
        [player.reset() for player in self.players]

    def mouse_pressed(self, x, y, button, mod):
        """
        called when a user clicks on the screen, passes the event to the menus / pages (which are still menus)
        """
        # If there is a current menu, (the game is not running)
        if self.visible_menu:
            # If the current menu is not the loading menu, pass the menu the mouse_pressed event
            if not self.visible_menu == "load_menu":
                menu = self.menus[self.visible_menu]
                menu.mouse_pressed(x, y, button, mod)
            # If the current menu is the loading menu, pass the current page the mouse_pressed event
            else:
                page = self.load_menu_pages[self.current_page]
                page.mouse_pressed(x, y, button, mod)

    def mouse_drag(self, x, y, dx, dy, button, mod):
        """
        called when a user drags the mouse with `button` held, passes the event to the menus
        """
        # If there is a menu
        if self.visible_menu:
            # pass if the menu is the loading menu, no sliders
            if self.visible_menu == "load_menu": return 0;
            # pass the event to the current menu
            menu = self.menus[self.visible_menu]
            menu.mouse_drag(x, y, dx, dy, button, mod)

    def start_game(self):
        """
        starts the game
        """
        # unpause the game, tell the program the game is running, set the last, current menus, fully reset the game
        self.is_paused = False
        self.is_running = True
        self.last_menu = self.visible_menu
        self.visible_menu = None
        self.full_reset()

    def save_game(self):
        """
        saves the game to a file in the ./saves/ directory
        files are named DDMMYY-HR_MIN_SEC.yaml (24 hours for the HR)
        """
        # Generate the save filename from the date / time
        filename = "./saves/" + strftime("%d%m%y-%H_%M_%S") + ".yaml"
        # generate the data to save from the data the game has about the current game :)
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
                    "color": self.player2.color},
                "fullscreen": self.window.fullscreen,
                "show_fps": self.show_fps,
                "options": self.options
            }
        # Save the data to the generated file
        with open(filename, "w") as file_:
            file_.write(dump_yaml(save_data))
        
        # set the current save variable 
        self.current_save = filename.split("/")[2]

    def load_game(self, filename):
        """
        loads the game from file `filename`
        """
        # Raise an error if the file's path is incorrect (not ".yaml", all save files are yaml files)
        if not filename.split('.')[1] == "yaml":
            raise ImportError(f"filename extension incorrect {filename.split('.')[1]}")

        def remove_duplicates(a, b):
            """
            removes all items that are in a from b and returns b
            a = [1, 2, 3, 4]
            b = [3, 4, 5, 6]
            c = remove_duplicates(a, b)
            c = [5, 6]
            """
            # raise an error if the given items aren't lists
            if not isinstance(a, list) and not isinstance(b, list):
                raise TypeError("a and b must be lists")

            # iterate over a, check if that item is in b, if it is, remove it from b
            for item in a:
                if item in b:
                    b.remove(item)

            return b

        # open the file
        with open("./saves/" + filename) as file_:
            # load the data from the yaml file
            yaml_data = load_yaml(file_.read())

            # raise an error if the save doesn't have something we need
            assert \
                "player1" and "player2" and "puck" and "fullscreen" and "show_fps" and "options" in yaml_data.keys(), \
                "Error importing the save, key datapoint missing"

            player1, player2 = yaml_data["player1"], yaml_data["player2"]
            puck = yaml_data["puck"]

            # load the options
            self.window.set_fullscreen(yaml_data["fullscreen"])
            self.toggle_show_fps(yaml_data["show_fps"])
            self.options = yaml_data["options"]

            # load the player1 object
            self.player1.pos = player1["pos"]
            self.player1.color = player1["color"]
            self.player1.score = player1["score"]

            # load the player2 object
            self.player2.pos = player2["pos"]
            self.player2.color = player2["color"]
            self.player2.score = player2["score"]

            # load the puck object
            self.puck.pos = puck["pos"]
            self.puck.vel = puck["vel"]
            self.puck.color = puck["color"]
        # set the current save, unpause
        self.current_save = filename
        self.unpause_game()

    def go_back(self):
        """
        goes to the previous menu
        """
        # If the menu we're leaving is the options, apply the options
        if self.visible_menu == "options": self.apply_options()
        # go back to the last menu
        self.visible_menu = self.last_menu

    def goto_mainmenu(self):
        """
        goes to the main menu
        """
        # pause the game, stop the game, tell the program we aren't playing a game, set the last, current menu vars
        self.is_paused = False
        self.is_running = False
        self.current_save = None
        self.last_menu = self.visible_menu
        self.visible_menu = "main_menu"

    def goto_loadmenu(self):
        """
        goes to the loading menu
        """
        # tell the player if there are no saves in the "./saves/" directory
        if len(listdir("./saves")) == 0: print("No saves"); return 0
        # build the menus
        self.build_load_menus()
        # so we can go back lmaoooo
        if not self.last_menu == self.visible_menu:
            self.last_menu = self.visible_menu
        self.visible_menu = "load_menu"


    def goto_options(self):
        """
        goes to the options menu
        """
        # pause the game
        self.is_paused = False
        # if the temp options file is empty, initialise the file
        if open("./resources/.temp_options.yaml").read() == '': self._init_temp_options()
        # load the options from the temp file or the current save file
        self.load_options()
        # set the last menu
        self.last_menu = self.visible_menu
        self.visible_menu = "options"

    def unpause_game(self):
        """
        unpauses the game / returns to the game from the pause menu
        """
        # tell the game we're playing, unpause, set the last menu
        self.is_running = True
        self.is_paused = False
        self.last_menu = self.visible_menu
        self.visible_menu = None

    def pause_game(self):
        """
        pauses the game / goes to the pause menu
        """
        # tell the game we're not playing, pause the game, set the last menu
        self.is_running = False
        self.is_paused = True
        self.last_menu = self.visible_menu
        self.visible_menu = "pause"

    def toggle_fullscreen(self):
        """
        toggles the fullscreen-ness of the game, obviously
        """
        # save the current options to the temp options file
        self.apply_options()

        # open the temporary file for the player, puck positions
        with open("./resources/.temp.yaml", "w") as file_:
            file_.write(
                dump_yaml(
                    {
                        # correct height for the players
                        "player1": self.player1.pos.y / self.window.height,
                        "player2": self.player2.pos.y / self.window.height,
                        # rationalise the position
                        "puck": Vector2D(
                            x=self.puck.pos.x / self.window.width,
                            y=self.puck.pos.y / self.window.height
                        )
                    }
                )
            )
        # toggle the window's fullscreen attribute
        self.window.set_fullscreen(not self.window.fullscreen)
        # reload the menus
        self.load_menus()
        # reload the options
        self.load_options()
        # reset the players (fix the x pos)
        [player.reset() for player in self.players]

        # open the puck, player temp file
        with open("./resources/.temp.yaml", "r") as file_:
            # load the data from yaml
            yaml_data = load_yaml(file_.read())
            # set the player1, 2 y positions / derationalise them
            self.player1.pos.y = yaml_data["player1"] * self.window.height
            self.player2.pos.y = yaml_data["player2"] * self.window.height

            # set the puck pos, derationalise
            self.puck.pos = yaml_data["puck"] * (self.window.width, self.window.height)


    def exit_game(self):
        """
        exits the game, performs cleanup
        """
        print("Exiting")
        # close the window
        self.window.close()
        # cleanup
        self._cleanup()
        # exit the program
        sysexit(0)

    def load_options(self):
        """
        Loads either the temp options or the options from the current save
        """
        # get the path for the file, either the temp options file or the current save
        filename = "./resources/.temp_options.yaml" if not self.current_save else f"./saves/{self.current_save}"
        
        # open the file
        with open(filename, "r") as file_:
            # load the data from yaml
            yaml_data = load_yaml(file_.read())
            # assertions
            try:
                assert isinstance(yaml_data, dict)
                assert "options" in yaml_data.keys()
            except AssertionError:
                raise ImportError("Save file corrupted")
            # set the games options to the loaded options
            self.options = yaml_data["options"]
        
        # commit the options
        self.options.set_options(self.menus["options"])

    def draw_current_menu(self):
        """
        draws the current menu, obviously
        If the current menu is the loading menu, it draws the current page in that menu
        """
        # if we have a menu up
        if self.visible_menu:
            # if the menu is the loading menu
            if self.visible_menu == "load_menu":
                # draw the current page, check the hovering for the buttons
                page = self.load_menu_pages[self.current_page]
                page.draw()
                for button in page.buttons:
                    if button.contains(self.mouse_position):
                        button.on_hover()
            # otherwise, draw the current menu, pass the mouse pos for hovering
            else:
                # print(self.visible_menu)
                menu = self.menus[self.visible_menu]
                menu.draw()
                for button in menu.buttons:
                    if button.contains(self.mouse_position):
                        button.on_hover()

    def mainloop(self, dt):
        """
        the main gameloop
        draws all the stuff, updates all the stuff
        """
        self.window.clear()

        if self.show_fps:
            self.fps_clock.draw()

        # if the game is running
        if self.is_running:
            # pause the game if the player hits P
            if self.keys[P]: self.pause_game(); self.load_menus()
            
            # motion, collision, drawing
            self.handle_motion()
            self.handle_collision()
            self.keep_in_bounds()
            self.puck.draw()
            self.puck.update()
            self.draw_scores()
            [player.draw() for player in self.players]
        # if the game is not running and not paused
        elif not self.is_paused:
            # draw the current menu
            self.draw_current_menu()

        # if the game is paused
        if self.is_paused:
            # draw the background, the current menu
            self.puck.draw()
            self.draw_scores()
            [player.draw() for player in self.players]
            self.draw_current_menu()
        # force the game to pause if the current menu is pause
        if self.visible_menu == "pause": self.is_paused = True
        # and vice versa
        else: self.is_paused = False

    def handle_motion(self):
        """
        handles the controls (moving each player up when they should)
        """
        # player 1 controls - W = UP, S = DOWN
        if self.keys[W]:    self.player1.move( 10)
        if self.keys[S]:    self.player1.move(-10)
        # player 2 controls - UP = UP, DOWN = DOWN
        if self.keys[UP]:   self.player2.move( 10)
        if self.keys[DOWN]: self.player2.move(-10)

    def handle_collision(self): 
        """
        handles the collision between the players and the puck
        kinda bad but its okish
        """
        for player in self.players:
            # this is a fitting comment
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
        """
        handles puck collision with the floor, cieling; handles scoring
        """
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
        """
        draws each player's score where it should
        """
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
        """
        loads all the menus from the ./menus/ directory into python objects I can work with
        """
        def get_slider_data(slider):
            """
            returns a tuple that contains all the data in the correct format to create a Slider object with
            """
            # these functions are just really dirty and looked gross to do 20 times so i made them functions
            x, y = slider["x"] * self.window.width, slider["y"] * self.window.height
            w, h = slider["w"] * self.window.width, slider["h"] * self.window.height
            min_, max_ = slider["min"], slider["max"]
            id_ = slider["id"]
            color = [int(num) for num in slider["color"].split(",")]
            return (x, y, w, h, min_, max_, color, id_)

        def get_button_data(button):
            """
            returns a tuple that contains all the data in the correct format to create a Button object with
            """
            x, y = button["x"] * self.window.width, button["y"] * self.window.height
            w, h = button["w"] * self.window.width, button["h"] * self.window.height
            text = button["text"]
            id_ = button["id"]
            function = self.functions[button["function"]]
            color = [int(num) for num in button["color"].split(",")]
            return (x, y, w, h, text, function, id_, color)

        # iterate through each file in the "./menus/" directory
        for filename in listdir("./menus"):
            # open the file
            with open("./menus/" + filename, "r") as file_:
                # load the yaml data
                yaml_data = load_yaml(file_)["menu"]
                # the name of the menu
                menu_name = yaml_data["name"]
                # initialise the menu, buttons, sliders, rgbsliders
                menu = Menu()
                buttons = None
                sliders = None
                rgbsliders = None

                # set vars if they exist
                if "buttons" in yaml_data.keys():
                    buttons = yaml_data["buttons"]
                if "sliders" in yaml_data.keys():
                    sliders = yaml_data["sliders"]
                if "rgbsliders" in yaml_data.keys():
                    rgbsliders = yaml_data["rgbsliders"]

                # if the menu has buttons, make a Button object and add it to the menu
                if buttons:
                    for key in buttons.keys():
                        button = buttons[key]
                        data = get_button_data(button)
                        multiline = button["multiline"] if "multiline" in buttons.keys() else False
                        menu.add_button(MenuButton(*data, multiline=multiline))

                # if the menu has sliders, make a Slider object and add it to the menu
                if sliders:
                    for key in sliders.keys():
                        slider = sliders[key]
                        data = get_slider_data(slider)
                        menu.add_slider(Slider(*data))

                # if the menu has rgbsliders, make an RGBSlider object and add it to the menu
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

                # add the menu to the menus dictionary with the key `menu_name`
                self.menus[menu_name] = menu

    def build_load_menus(self):
        """
        builds the load menu pages procedurally
        needs rewritten probably but i'll cross that bridge when i get to it
        """
        # the total number of pages in the menu
        TOTAL_PAGES = (len(listdir("./saves")) / 5)
        # if it's not a whole number
        if TOTAL_PAGES % 1 != 0.0:
            # round it up
            TOTAL_PAGES = int(TOTAL_PAGES) + 1
            EVEN_PAGES = False
        # if it is a whole number (amount of pages % 5 == 0)
        else:
            # Convert the x.0 float into int x
            TOTAL_PAGES = int(TOTAL_PAGES)
            EVEN_PAGES = True
        # make a new page
        page = Menu()

        def commit_page(page, page_number):
            """
            adds the page to the pages array
            """
            # if it's not the first page, add a back button that takes you to the last page you were at (page 2 -> page 1)
            if page_number != 0:
                # last page button
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

            # if the page isn't the last one, add a forward button (page 1 -> page 2)
            if page_number != TOTAL_PAGES - 1:
                # next page button
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

            # add the page to the pages dictionary w/ the page number as the key
            self.load_menu_pages[page_number] = page

        # enumerate the pages & saves sorted by save names
        for index, save in sorted(enumerate(listdir("./saves"))):

            # the page number is the index of the save in "./saves/" floor divided by 5
            # index 8 (the 9th save) = page 2 (8 // 5 = 1 (indexes from 0))
            page_number = index // 5

            # get the x, y, w, h for the save file buttons
            x = 0.50 * self.window.width
            y = load_menu_ratios[index % 5] * self.window.height
            w = 0.25 * self.window.width
            h = 0.10 * self.window.height

            # the x position for the delete button, it uses the y and h from the file button for y, w, and h
            del_x = 0.685 * self.window.width

            # add the delete button to the menu
            page.add_button(MenuButton(del_x, y, h, h, "x", self.delete_save, color=MID_GRAY, id_=f"delete game - {save}", function_args=save))
            # add the load button to the menu
            page.add_button(MenuButton(x, y, w, h, save.split('.')[0], self.load_game, color=MID_GRAY, id_=f"load_game - {save}", function_args=save))
            # if we fill a menu (5 load buttons, 5 delete buttons), commit the page, make a new page
            if len(page.buttons) == 10:
                commit_page(page, page_number)
                page = Menu()

        # if our pages don't divide evenly, we'll have extra save files to draw,
        # so we commit the remaining page 
        if not EVEN_PAGES:
            commit_page(page, page_number)

    def delete_save(self, filename):
        """
        deletes the save
        """
        # delete the save file
        rm("./saves/" + filename)
        # if we don't have any saves, go back 
        if len(listdir("./saves"))== 0:
            self.go_back()
            print("No saves")
        # if we clear a page, go to the previous page
        elif len(listdir("./saves")) % 5 == 0:
            self.build_load_menus()
            self.goto_load_menu_page(self.current_page - 1)
        # otherwise, refresh the menu
        else:
            self.build_load_menus()



    def goto_load_menu_page(self, page_number):
        """
        goes to the page number `page_number`
        """
        # if the page number is -1, go back
        if page_number == -1: self.go_back()
        # if the page number is not in the pages dictionary, raise an error
        if not page_number in self.load_menu_pages.keys(): raise ValueError("page_number incorrect")
        # set the current page to the new one
        self.current_page = page_number
