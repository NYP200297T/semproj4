import pathlib
from sense_hat import SenseHat

green = [0, 255, 0]
yellow = [255, 255, 0]
blue = [0, 0, 255]
red = [255, 0, 0]
white = [255,255,255]
nothing = [0,0,0]
pink = [255,105, 180]
gold = [255, 215, 0]
orange = [255,165,0]
purple = [255,0,255]

sense = SenseHat()

def filepather(filename):
  return f'{pathlib.Path(__file__).parent}/assets/{filename}'

mazes = [filepather(f'mazes/maze{i}.png') for i in list(range(1,7))]
for maze in mazes:
    maze = sense.load_image(maze,redraw=False)
    print(maze)
    print([i for i in maze if i == blue])
    print([i for i in maze if i == red])