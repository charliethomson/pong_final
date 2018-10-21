from src.game import Game
from include.vector2d import Vector2D
from pyglet.window import key, mouse, Window
from pyglet.clock import schedule_interval
from pyglet.app import run as run_game
from pyglet.image import load

favicon = load("./resources/favicon.png")
keys = key.KeyStateHandler()
window = Window(1000, 1000)
window.set_icon(favicon)
window.set_caption("Pong v1.4")
window.push_handlers(keys)
game = Game(window, keys)

@window.event
def on_mouse_motion(x, y, dx, dy):
    print(x, y)
    game.mouse_position = Vector2D(x, y)

@window.event
def on_mouse_press(x, y, button, mod):
    game.mouse_pressed(x, y, button, mod)

@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    game.mouse_drag(x, y, dx, dy, button, mod)

schedule_interval(game.mainloop, 1/60.0)
if __name__ == "__main__":
    run_game()
