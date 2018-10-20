
class Options:
    def __init__(self, player1_color=(255, 255, 255), player2_color=(255, 255, 255), puck_color=(255, 255, 255), is_fullscreen=False, difficulty=9):
        self.player1_color = player1_color
        self.player2_color = player2_color
        self.puck_color    = puck_color
        self.is_fullscreen = is_fullscreen
        self.difficulty    = difficulty
        
 
    def set_difficulty(self, value):
        if isinstance(value, int):
            self.difficulty = value
        else: raise TypeError("cannot set difficulty to non-integer value")

    def set_fullscreen(self, mode: bool):
        if isinstance(mode, bool):
            self.is_fullscreen = mode
        else: raise TypeError("cannot set fullscreen to non-boolean value")

    def set_player1_color(self, color: (list, tuple)):
        if isinstance(color, (list, tuple)):
            self.player1_color = color
        else: raise TypeError("cannot set player1_color to non-list or non-tuple value")

    def set_player2_color(self, color: (list, tuple)):
        if isinstance(color, (list, tuple)):
            self.player2_color = color
        else: raise TypeError("cannot set player2_color to non-list or non-tuple value")
        
    def set_puck_color(self, color: (list, tuple)):
        if isinstance(color, (list, tuple)):
            self.puck_color = color
        else: raise TypeError("cannot set puck_color to non-list or non-tuple value")
    
    def apply_settings(self, game):
        options_menu = game.menus["options"]
        game.player1.color = self.player1_color
        game.player2.color = self.player2_color
        game.puck.color = self.puck_color
        game.puck.magnitude = self.difficulty
        game.window.set_fullscreen(self.is_fullscreen)
