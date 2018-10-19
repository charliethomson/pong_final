This is a pong game using pretty much only pyglet.
I made all the interface classes myself, (Rect, Slider, Button, etc.), and pyglet handles the drawing and windowing.
The game was pretty easy to write after I decided on sizes for the paddles, puck.
The menus are where it took a turn for the worse.
The code is all over the place, and I know I called it final, but I think I'm going to have to re-re-rewrite it
The load game function doesn't work, it just resets the game. I plan to have a menu pop up and have buttons and info boxes that show the data in the save - but it's in the works
To run:
	(make sure you have python3, and a somewhat recent version of pyglet installed)
	cd into the folder you have the files saved in
	run python3 main.py
	and it'll put you at the main menu
