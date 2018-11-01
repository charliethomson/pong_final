from src.game import Game

from include.vector2d import Vector2D

from pyglet.app import run as run_game
from pyglet.clock import schedule_interval
from pyglet.window import mouse, Window
from pyglet.window.key import KeyStateHandler

keys = KeyStateHandler()
window = Window(1000, 1000)
window.push_handlers(keys)
game = Game(window, keys)
game.setup()

@window.event
def on_mouse_motion(x, y, dx, dy):
    game.mouse_position = Vector2D(x, y)

@window.event
def on_mouse_press(x, y, button, mod):
    game.mouse_pressed(x, y, button, mod)

@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    game.mouse_drag(x, y, dx, dy, button, mod)

@window.event
def on_close():
    game.exit_game()


schedule_interval(game.mainloop, 1/60.0)
run_game()
