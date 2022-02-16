# Setting Imports
from sense_hat import SenseHat          # For SenseHat
from adafruit_crickit import crickit    # For CrickitHat
from PIL import Image                   # For Images
import numpy as np                      # For Array
from pygame import mixer                # For Music
import time                             # For Time
import random                           # For Randomisation
import pathlib                          # Finding path of files
from math import floor                  # Function for Rounding Down number

sense = SenseHat()          # Initialise SenseHat
sense.low_light = False     # Set the Led to normal brightness

ss = crickit.seesaw         # Initialise CrickitHat Ports
irsensor = crickit.SIGNAL8  # Initialise IR sensor to signal 8

# Initialise cricket drivers for servo 4
# Servo min angle 0 deg, max angle 171 deg
servo = crickit.servo_4
servo.actuation_range = 180
servo.set_pulse_width_range(600,2450)
servo.throttle = 100
servo.angle = 180

# Initialise Buzzer
buzzer = crickit.drive_1
# Beep once at Start
buzzer.fraction = 0.01
time.sleep(0.5)
buzzer.fraction = 0.0

# Initialise music player
mixer.init()
mixer.music.set_volume(0.5)

# Initialise Colours
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

# Misc lists
colours = [green, yellow, red, pink, orange, purple] # Extra Colours used
secretkey = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right'] # For Hell Mode

# Mode settings - Parameters
easy_mode = {
  'pic': 'levels/easy.png',                                    # Game Images for Easy Mode
  'car': {'rounds': 50, 'movement': 1, 'spacing': 12},        # Number of iterations, Movement Speed for User, Min Spacing Btw Obstacles
  'snake': {'rounds': 5, 'movement': 2},                       # no. of fruits, Time for refreshing stage
  'bounce': {'rounds': 100, 'movement': 2, 'bouncesize': 4, 'chance': 10},    # No. of iterations,Speed of ball ,Size of User Bar Platform, Chance of generating obstacle
  'maze': {'rounds': 2, 'time': None},                         # No. of Maze Stages, Time limit for clearing maze
  'shooter': {'rounds': 5, 'time': 2.0, 'lives':3},            # No. of Shooting Rounds, Time for Reaction, No. of User lives
  'reaction': {'rounds': 4, 'time': 3.0}                       # No. of Rounds, time for user to react
}

normal_mode = {
  'pic': 'levels/normal.png',
  'car': {'rounds': 100, 'movement': 4, 'spacing': 10}, #pixels (1 per second)
  'snake': {'rounds': 10, 'movement': 5}, #no. of fruit
  'bounce': {'rounds': 200, 'movement': 10, 'bouncesize': 3, 'chance': 30}, #waves
  'maze': {'rounds': 3, 'time': 60},
  'shooter': {'rounds': 5, 'time': 1.5, 'lives':3},
  'reaction': {'rounds': 8, 'time': 1.0}
}

hell_mode = {
  'pic': 'levels/hell.png',
  'car': {'rounds': 300, 'movement': 10, 'spacing': 8}, #pixels (1 per second)
  'snake': {'rounds': 10, 'movement': 10}, #no. of fruits before last one
  'bounce': {'rounds': 200, 'movement': 20, 'bouncesize': 3, 'chance': 80}, #waves
  'maze': {'rounds': 10, 'time': 30},
  'shooter': {'rounds': 10, 'time': 0.8, 'lives':1},
  'reaction': {'rounds': 16, 'time': 0.5}
}

# Misc functions
def clamp(value, min_value=0, max_value=7): # Limits number in range
    return min(max_value, max(min_value, value))

def blink_screen(screen,times): # For blinking Screen
  for _ in range(times):
    sense.set_pixels(screen)
    time.sleep(1)
    sense.clear()
    time.sleep(1)

def index_to_coords(index): # Convert Screen Index to Coords
  x = index%8
  y = floor(index/8)
  return [x,y]

def chunks(lst, n):  # Splits a list evenly to number of lists
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def numbersign(number): # Return Positive/Negative of a Number
  if number >= 0:
    return 1
  else:
    return -1

def filepather(filename): # Return filepath to assets
  return f'{pathlib.Path(__file__).parent}/assets/{filename}'

def findcoords(screen,value): # Find Specific Value in the screen
  return screen.index(list(value))

def returncoords(screen,value): # Find Multiple Values in the Screen
  return [i for i in range(len(screen)) if screen[i] == value]

def screenreplace(screen,value,coords): # Replace Specific Value on the screen at certain coords
  screencoord = coords[0]*8 + coords[1]
  screen[screencoord] = value
  return screen

def presstime(presstime,exptime):  # Check if joystick presstime is higher than given reaction time - For Reactioner and Wild Wild West Bang
  if exptime == None or presstime == None:
    return False
  else:
    if presstime > exptime:
      return True
    else:
      return False

def countdown(): #screen countdown
  sense.show_letter('3')
  time.sleep(1)
  sense.show_letter('2')
  time.sleep(1)
  sense.show_letter('1')
  time.sleep(1)
  sense.clear()

def preexitprogram(): # Reset Music and Reset Motor to Initial postition
  mixer.music.unload()
  mixer.music.stop()
  sense.clear()
  buzzer.fraction = 0.0
  servo.angle = 180

warning = sense.load_image(filepather('warning.png'),redraw=False) # Warning Image - For Hell Mode

# Games as functions
def race(mode):
  # race capacitor broken
  # Setting Crazy Racer Parameters Based on Difficulty Mode from Main Function
  speed = mode['car']['movement']
  dist = mode['car']['rounds']
  spacing = mode['car']['spacing']

  mixer.music.load(filepather('sound/dejavu.mp3'))    # Load Music
  sense.clear(nothing) # Clear Screen

  # Starting Game Screen
  X = blue
  O = nothing
  showscreen = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, X, X, O, O, O, O,
    O, O, X, X, O, O, O, O,
    O, O, X, X, O, O, O, O
    ]
  sense.set_pixels(showscreen)

  # Internal Initial Variables
  cooldown = [-1]*4
  carcolours = colours
  carrows = {u:[] for u in list(range(4))}

  # Making Car obstacles
  # Generate front position of the car obstacles
  for i in range(dist-8):           # remove last 8 Distance for final area
    rows = list(range(4))           # Setting 4 Rows
    for _ in range(4):              # Loop 4 Times
      r = random.choice(rows)       # RANDOMISE ROW 1-4 PER LOOP
      rows.remove(r)                # Remove Row From Choice

      if cooldown[r] == 0:          # put back colours that are cleared from board
        carcolours.append(carrows[r][i-spacing])

      if len([u for u in cooldown if u > 1]) >= 3:    # Limit only 3 cars obstacles in the 4 rows
        carrows[r] = carrows[r] + [nothing]           # put nothing
        continue

      if cooldown[r] <= 0 and random.randint(1,100) <= 10+(80/(dist-i)):  # randomise chance to spawn car

          if carcolours != []:          # check if there's a colour available to spawn taken from colours list (Line 56).
            cooldown[r] = spacing       # Reset Cooldown
            chosencol = random.choice(carcolours)    # Randomise the chosen Colour
            carcolours.remove(chosencol)             # Remove chosen colour from the colours list (Line 56).
            carrows[r] = carrows[r] + [chosencol]    # Add colour to the car obstacle in the row
          else:
            carrows[r] = carrows[r] + [nothing]      # Set Nothing
      else:
        carrows[r] = carrows[r] + [nothing]          # Set Nothing

    cooldown = [i-1 for i in cooldown]  # For Every Loop cooldown once

  # Complete a 3x1 car obstacle in the specific position
  counterdown = 0
  selectcol = None
  for rower in list(carrows.keys()):              # For each generated row
    carrows[rower] = [nothing]*6 + carrows[rower] + [nothing]*8     # Initialise row
    for indexer in range(len(carrows[rower])):    # For Each point in the row

      if counterdown <= 0:        # once done with car spawn
        colour = carrows[rower][indexer]
        if colour != nothing:
          counterdown = 2
          selectcol = colour      # set to colour for next 2 pixels
      elif selectcol != None:     # if still spawning car
        carrows[rower][indexer] = selectcol
        counterdown -= 1

      if counterdown == 0: # once done spawn, reset
        selectcol = None

    carrows[rower] = carrows[rower] + [gold]*8 # add last rows as gold

  screenlist = []
  for i in range(len(carrows[1])-7): # take length of rows
    makescreen = []
    for rower in list(carrows.keys()):
      selectpix = carrows[rower][i:i+8]
      selectpix.reverse()
      makescreen = makescreen + [selectpix]*2

    newscreen = [[makescreen[y][u] for y in range(8)] for u in range(8)] # rotate screen
    newscreen = [j for i in newscreen for j in i] # extract RGB values from rows

    screenlist.append(newscreen)


  # Player inputs, show screens
  player = 1
  mixer.music.play(loops=-1) # Start and loop music - Deja Vu
  for est in range(len(screenlist)):
    screen = screenlist[est]
    exptime = time.time() + 1/speed
    breakout = True
    while breakout:
      for event in sense.stick.get_events():
        if presstime(event.timestamp, exptime) == True:
          breakout = True
          break
        if event.action != 'released':
          if event.direction == 'left':       # When User press left on the joystick
            player -= 1
            breakout = False
            break
          elif event.direction == 'right':    # When User press right on the joystick
            player += 1
            breakout = False
            break
      if presstime(time.time(),exptime):
        break
    player = clamp(player,0,3)
    playerpix = [40+(player*2), 41+(player*2), 48+(player*2), 49+(player*2), 56+(player*2), 57+(player*2)]
    collision = [i for i in playerpix if screen[i] != nothing and screen[i] != gold]

    # if player collides with car obstacles
    if len(collision) > 0:
      sense.set_pixels(screen)
      return 'gameover' # End Game

    screen = [blue if c in playerpix else screen[c] for c in range(64)] # Updates player position
    sense.set_pixels(screen)

  return 'win' # Player Reach the end.

def snake(mode):
  # Setting Snake-E Parameters Based on Difficulty Mode from Main Function
  speed = 1/mode['snake']['movement']
  rounds = mode['snake']['rounds']

  # Starting Game Screen
  X = blue
  O = nothing

  showscreen = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    X, O, O, O, O, O, O, O,
    X, O, O, O, O, O, O, O,
    X, O, O, O, O, O, O, O
    ]

  # Initialise Snake Position
  snake = [40,48,56]
  x_direction = 0
  y_direction = -1
  showscreen = [showscreen[i] if i not in snake else blue for i in range(len(showscreen))]

  # Initialise Music
  mixer.music.load(filepather('sound/estart.mp3'))
  mixer.music.queue(filepather('sound/eloop.mp3'),loops=-1)
  mixer.music.play()

  # For every round after snake eat a fruit
  for r in range(rounds):
    # Setting a fruit at Random Position
    emptpypix = returncoords(showscreen,nothing)
    fruit = random.choice(emptpypix)
    if r != rounds-1:    # Show fruit colour based no. of rounds
      showscreen[fruit] = green
    else:
      showscreen[fruit] = gold

    # Check the snake position, user input and update the screen
    while True:
      showscreen = [showscreen[i] if i not in snake else nothing for i in range(len(showscreen))] # Show Snake on Led Screen
      accel = sense.get_accelerometer_raw()   # Initialise Accelerometer
      head = snake[0]       # Set the head of the snake

      # Check Accelerometer Values for x
      if abs(accel['x']) > abs(accel['y']) and abs(accel['x']) > 0.1:   # Check if value is larger than 0.1 (For horizontal tilting)
        if numbersign(accel['x']) != x_direction and y_direction != 0:
          x_direction = numbersign(accel['x'])
          y_direction = 0

      # Check Accelerometer Values for y
      elif abs(accel['y']) > abs(accel['x']) and abs(accel['y']) > 0.1: # Check if value is larger than 0.1 (For vertical tilting)
        if numbersign(accel['y']) != y_direction and x_direction != 0:
          x_direction = 0
          y_direction = numbersign(accel['y'])

      # Based on Accelerometer Value, make snake move to specific direction
      if head%8 == 0 and x_direction == -1:
        head += 7
      elif (head+1)%8 == 0 and x_direction == 1:
        head -= 7
      else:
        head += x_direction

      if head in range(0,8) and y_direction == -1:
        head += 56
      elif head in range(56,64) and y_direction == 1:
        head -= 56
      else:
        head += (y_direction*8)

      # When snake eat fruit
      if fruit == head:
        snake = [head] + snake
      else:
        snake = [head] + snake[:-1]
      # Update Screen
      showscreen = [showscreen[i] if i not in snake else blue for i in range(len(showscreen))]
      sense.set_pixels(showscreen)

      # if snake eats fruit go to next round
      if fruit == head: # set screen before breaking out of round
        buzzer.fraction = 0.05
        break

      # Check if snake hits itself
      if len(snake) != len(set(snake)): # check dupes
        return 'gameover'

      # Update Screen Timing
      time.sleep(speed)
      buzzer.fraction = 0.0

  return 'win'

def maze(mode):
  # Setting Maze Explorer Parameters Based on Difficulty Mode from Main Function
  rounds = mode['maze']['rounds']
  sleeper = mode['maze']['time']

  # Init Variables
  sense.clear(nothing)
  mazes = [filepather(f'mazes/maze{i}.png') for i in list(range(1,7))]

  # Setting Maze Stage with Given imported Maze Picture
  for i in range(rounds):
    buzzer.fraction = 0.0
    choosemaze = random.choice(mazes)
    maze = sense.load_image(choosemaze,redraw=False)
    maze = [i if i != [0,50,255] else [0,0,255] for i in maze] # fix bad blues
    # Starting Values of Specific maze
    player = findcoords(maze,blue)
    endpoint = findcoords(maze,red)
    barrier = returncoords(maze,white)

    # Setting Endpoint for last Round of Maze
    if i == rounds-1:
      maze[endpoint] = gold
    sense.set_pixels(maze)

    # Set Time Limit if have (Hell Mode)
    if sleeper != None:
      exptime = time.time() + sleeper
    else:
      exptime = None

    # User Input for moving thru maze
    nobreak = True
    while nobreak:
      for event in sense.stick.get_events():
        if presstime(event.timestamp, exptime) == True:
          return 'gameover'

        # User Movements based on Input on Joystick
        if event.action != 'released':
          if event.direction == 'right':
            if (player+1)%8 != 0:             # Check if player is on the most right
              templayer = player + 1          # Move Right Once
          elif event.direction == 'left':
            if player%8 != 0:                 # Check if player is on the most left
              templayer = player - 1          # Move left Once
          elif event.direction == 'up':
            if player not in range(0,8):      # Check if player is on the first row
              templayer = player - 8          # Move up Once
          elif event.direction == 'down':
            if player not in range(56,64):    # Check if player is on the last row
              templayer = player + 8          # Move down Once
          else:
            continue

          # Check for Collision of user and Maze Walls
          if templayer not in range(0,64) or templayer in barrier:
            continue

          # Beep buzzer once
          buzzer.fraction = 0.01
          time.sleep(0.05)
          buzzer.fraction = 0.0

          # Update Player Position
          maze[player] = nothing
          maze[templayer] = blue
          player = templayer

          sense.set_pixels(maze) # Update screen with specific Maze

          # For clearing a Maze Round
          if player == endpoint:
            nobreak = False
            break

    sense.clear() # Clear Screen

  return 'win' # Winning Game

def shooter(mode):
  # Setting parameters for Wild Wild West Bang Based on Difficulty Mode from Main Function
  rounds = mode['shooter']['rounds']-1
  sleeper = mode['shooter']['time']
  livescount = mode['shooter']['lives']

  # Initialise game Variables
  lives = [i+56 for i in list(range(livescount))]
  playergun = [32,33,34,40]
  press = []
  cooldown = False

  # load Music
  mixer.music.load(filepather('sound/pewpew.mp3'))

  # For each round
  for r in range(rounds):

    mixer.music.play(loops=-1)  # play Music

    shot = False
    # Showing the Starting animation of Game
    for p in range(1,4):
      gunner = sense.load_image(filepather(f'gunner/{p}.png'),redraw=False)
      if r == rounds-1: # check last round
        gunner = [gold if i == red else i for i in gunner] # set enemy to gold

      sense.set_pixels(gunner) # show zoom out
      time.sleep(1)

      # Set Player Life on Screen
      gunner = [blue if c in lives else gunner[c] for c in range(len(gunner))]

    # Time for Shooting (within 30 Secs)
    for sec in range(1,31): # timer
      # Moving of Servo
      servo.angle = 180 - 6*(sec+1)

      # Events Happening
      if cooldown == False:   # if either greenscreen or buzzer activates, activate for aleast 1 sec - Cooldown is Misc Function
        press = []
        chance = round((sec/30)*100,ndigits=1)         # Chance of Events to happen increases as time goes on ( Buzzer or Green Screen)
        randscreen = random.randint(1,100)             # Random Number Generated
        if chance >= float(randscreen):                # If the chance is more than the random number generated
          gunner = [green if i == nothing else i for i in gunner] # set background to green
          press = [True]
        else:
          gunner = [nothing if i == green else i for i in gunner] # reset green background
          press = [False]

        randbuzz = random.randint(1,100)              # Random Number Generated
        if chance >= float(randbuzz):                 # If the chance is more than the random number generated
          buzzer.fraction = 0.05                      # Buzz Beep
          press = press + [True]
        else:
          buzzer.fraction = 0.0                       # Off Buzzer
          press = press + [False]
      else:
        press = [False]*2
        cooldown = False

      # Update Screen
      sense.set_pixels(gunner)             # Display Player

      # Wait for User input
      exptime = time.time() + sleeper     # Reaction Time
      savetime = time.time()              # Start Time of listening to reaction time
      nobreak = True
      if all(press): # Stop Music, when Both green screen and buzzer is active
        mixer.music.pause()

      if press[0] or press[1]: # Listen to input if either green screen or buzzer is active
        cooldown = True
        while nobreak:

          for event in sense.stick.get_events():

            if event.timestamp < savetime:  # Ignore Inputs until event happens
              continue

            # Check user pressed Joystick
            if event.action != 'released':    # if User Pressed joystick
              buzzer.fraction = 0             # Off Buzzer
              shot = True
              nobreak = False
              # If user press faster than specific reaction time
              if all(press) and presstime(event.timestamp, exptime) == False:
                gunner = [nothing if i == green or i == red or i == gold else i for i in gunner] # kill red and go next round
                break
              else: # If user press slower than specific reaction time
                gunner[lives[-1]] = nothing             # remove 1 life
                lives = lives[:-1]
                gunner = [nothing if gunner[i] == green or i in playergun else gunner[i] for i in range(len(gunner))] # kill player and go next round
                break
          # if user never pressed joystick and specific reaction time is over
          if all(press) and presstime(time.time(), exptime):
            gunner[lives[-1]] = nothing
            lives = lives[:-1]
            gunner = [nothing if gunner[i] == green or i in playergun else gunner[i] for i in range(len(gunner))] # kill player and go next round
            break
          elif presstime(time.time(), exptime) and nobreak == True:
            break

      # Update Final Screen before next round
      sense.set_pixels(gunner)
      time.sleep(2)

      # Check if Win or Lose based on Life Value
      if len(lives) == 0:
        return 'gameover'

      if all(press) or shot: # Move to next round
        break

  return 'win'

def ballblaster(mode):
  # Setting Ball Blaster Game Parameters Based on Difficulty Mode from Main Function
  mode        = mode['bounce'] # initiate dict from mode
  rounds      = mode['rounds']
  movement    = mode['movement']
  bouncesize  = mode['bouncesize']
  chance      = mode['chance']

  # Initialise Variables
  buzzer.fraction = 0.0

  lower = 200    # Furthest Distance to Player's platform
  upper = 700    # Closest Distance to Player's platform

  playerzone = [(8*i)-1 for i in range(1,9)]        # list of player bounce coords
  possiblepos = 8-bouncesize+1                      # Possible no. of spots for platform to move
  irrange = int(round((upper-lower)/possiblepos))   # Range of IR sensor Values - One spot

  irranges = [lower+irrange*i for i in range(possiblepos)] # Range of IR sensor Values - A list of all the spots

  # Initial Values for Ball
  ballpix = 54
  x_direction = -1 # x,y movement
  y_direction = -1
  coords = [6,6]
  colourdict = {} #key=index, value=colour

  # Initialise Variables
  screen = [nothing]*64
  prevind = 0

  # Monitor Distance of the Ball
  for _ in range(rounds): # distance mode

    x_directions = 0
    y_directions = 0

    # Randomise Generation of Obstacles
    tempcolourlist = [i for i in colours if i not in colourdict.values()]  # takes colours list without generated colours
    if len(tempcolourlist) != 0 and random.randint(0,100) <= chance:       # Randomise chance of generating coloured obstacle
      # Choose a random spot from 1st to 6th column
      randscreen = [i for i in range(len(screen)) if screen[i] == nothing and index_to_coords(i)[0] < 6 and index_to_coords(i)[0] not in list(range(coords[0]-1,coords[0]+2)) and index_to_coords(i)[1] not in list(range(coords[1]-1,coords[1]+2))]
      randscreen = random.choice(randscreen)
      # Places a random colour at the spot
      randcolour = random.choice(tempcolourlist)
      colourdict[randscreen] = randcolour
      screen[randscreen] = randcolour

    screen = [nothing if i == blue or i == white else i for i in screen] # Clear Ball and platform

    # Reading IR Value and Set player's platform to specific location
    irdist = ss.analog_read(irsensor)  # 700 = close, 200 = far
    for ind in range(len(irranges)):
      if ind != len(irranges)-1:       # Ignore last one in the IR ranges list
        if irdist >= irranges[ind] and irdist <= irranges[ind+1]:  # Check if current IR values is in the range
          break

    # Initialise Variables
    playerpix = playerzone[ind:ind+bouncesize]
    tempcoords = [coords[0]+x_direction, coords[1]+y_direction]

    # Check Collision with Player's platform
    if tempcoords[0] == 7 and (coords[1] in range(ind,ind+bouncesize) or coords[1] in range(prevind,prevind+bouncesize)): # check if bouncer is to right of ball
      x_directions += 1           # Reverse x-direction
      buzzer.fraction = 0.01      # Beep once
    if tempcoords[0] < 0:         # check if ball is to left of screen edge
      x_directions += 1           # Reverse x-direction
      buzzer.fraction = 0.01      # Beep once
    if tempcoords[0] > 7:         # check if ball misses platform
      return 'gameover'           # Player Loses
    if tempcoords[1] < 0 or tempcoords[1] > 7:  # check if ball hit either top or bottom
      y_directions += 1           # Reverse y-direction
      buzzer.fraction = 0.01      # Beep once

    # Check Collision with obstacles
    for indexer in [*colourdict]:           # cycles around temporary list of colourdict iteratables so won't be affected by changes to colourdict in loop
      indexcoords = index_to_coords(indexer)    # Convert Index to screen coordinates
      temptempcoords = tempcoords               # Simulate New Coords
      # Check if Directions are reversed
      if x_directions == 1:
        temptempcoords[0] = coords[0] - x_direction
      if y_directions == 1:
        temptempcoords[1] = coords[1] - y_direction

      if temptempcoords == indexcoords:         # Check if ball collides with obstacles
        x_directions += 1
        y_directions += 1
      elif indexcoords[0] == coords[0]+x_direction and indexcoords[1] == coords[1] and x_direction != 0:  # Check if ball collides with obstacles diagonally (x)
        x_directions += 1
      elif indexcoords[0] == coords[0] and indexcoords[1] == coords[1]+y_direction and y_direction != 0:  # Check if ball collides with obstacles diagonally (y)
        y_directions += 1
      else:
        continue

      screen[indexer] = nothing  # Remove obstacles from screen
      del colourdict[indexer]    # Remove obstacles from Dict
      buzzer.fraction = 0.01     # Buzzer Beep

    # For Movement of the ball
    if x_directions != 2:        # check if x_directions negate each other
      if x_directions == 1:
        x_direction = -x_direction
      coords[0] = coords[0]+x_direction

    if y_directions != 2:        # check if y_directions negate each other
      if y_directions == 1:
        y_direction = -y_direction
      coords[1] = coords[1]+y_direction

    # Update Game Screen
    ballpix = coords[0] + coords[1]*8   # For Ball Index
    screen[ballpix] = white             # Set Ball Colour
    screen = [blue if i in playerpix else screen[i] for i in range(len(screen))] # Set Player's Platform
    prevind = ind
    sense.set_pixels(screen)   # Show Screen with platform and Ball

    # Update Screen Speed
    time.sleep(1/movement)
    buzzer.fraction = 0.0
  return 'win'

def reaction(mode):
  # Setting Parameters for Reactioner Based on Difficulty Mode from Main Function
  rounds = mode['reaction']['rounds']
  sleeper = mode['reaction']['time']
  score = {'win':0,'lose':0}

  # Init Variables
  directions = ['up','down','left','right','middle']
  pointscreen = [nothing]*16

  # Number of Rounds
  for r in range(rounds):
    # Choosing a random Direction
    direct = random.choice(directions)

    sense.clear() # Clear Screen
    time.sleep(1) # Wait 1 Sec
    time.sleep(random.random()*4) # randomise Timing btw 0-4 Secs
    sense.load_image(filepather(f'directions/{direct}.png')) # Load given Direction Image
    buzzer.fraction = 0.01

    # Set Reaction Time
    if sleeper != None:
      exptime = time.time() + sleeper   # Reaction Time
      savetime = time.time()            # Start Time of listening to reaction time
    else:
      exptime = None
      savetime = None

    # User Input on Joystick
    nobreak = True # Wait for user to press
    while nobreak:
      for event in sense.stick.get_events():

        if presstime(savetime, event.timestamp) == True:  # If user press faster than Start Time of listening to reaction time
          continue

        if presstime(event.timestamp, exptime) == True:   # If user press slower than specific reaction time
          score['lose'] += 1
          pointscreen[r] = red
          nobreak = False
          break

        # Check if user pressed correct direction on the joystick
        if event.action == 'pressed':

          if event.direction == direct: # if correct
            score['win'] += 1           # increase score (win)
            pointscreen[r] = green      # Set Index in list to green
          else:                         # if wrong
            score['lose'] += 1          # increase score (lose)
            pointscreen[r] = red        # Set Index in list to red

          nobreak = False
          break

      if presstime(time.time(), exptime) and nobreak == True:  # if never press in time/never press
        score['lose'] += 1         # increase score (lose)
        pointscreen[r] = red       # Set Index in list to red
        nobreak = False            # break out of loop

    # Show Score Screen after each round
    buzzer.fraction = 0.0         # Off buzzer
    showscreen = np.array(list(chunks([np.uint8(i) for i in pointscreen],4)))   # Convert point index list to numpy array
    showscreen = Image.fromarray(showscreen,mode='RGB')                         # Convert Numpy Array to image object
    showscreen = showscreen.resize((8,8),Image.BOX)                             # Resize 4x4 image to 8x8 image
    showscreen = [list(r) for i in list(np.asarray(showscreen)) for r in i]     # Convert Numpy Array to list of screen colours
    sense.set_pixels(showscreen)          # Show point screen
    time.sleep(4)

  # Winning Criteria
  if score['win'] > score['lose']: # If more wins than lose
    return 'win'                   # Win Game
  else:                            # if more lose than win
    return 'gameover'              # Lose Game

def main():
  # Show Image and Start Music for Startup of Hachi-Bit Archive
  mixer.music.load(filepather('sound/startup.mp3'))   # Load Music
  mixer.music.play()
  sense.load_image(filepather('8.png'))               # Load Image
  time.sleep(10)                  # unload Image
  mixer.music.stop()
  mixer.music.unload()            # unload music

  # Selection difficulty mode for game
  lvls = {'easy': easy_mode, 'normal': normal_mode}
  sense.show_message(text_string='Choose Difficulty',scroll_speed=0.04)

  # Initialise Variables
  chooselvl = 0
  chosen = True
  newlvler = True
  seecount = 0

  # Loop of Choosing Difficulty
  while chosen:

    #Check if new difficulty is chosen
    if newlvler == True:
      lvl = list(lvls.keys())[chooselvl]
      sense.load_image(filepather(lvls[lvl]['pic']))    # Image for Difficulty
      newlvler = False

    # User Input for Difficulty
    breakout = True
    while breakout:
      for event in sense.stick.get_events():
        if event.action == 'pressed':
          if event.direction == 'left':       # When User press left on the joystick switch diff
            chooselvl += 1
            newlvler = True
          elif event.direction == 'right':    # When User press right on the joystick switch diff
            chooselvl -= 1
            newlvler = True
          elif event.direction == 'middle':   # When User press middle on the joystick select diff
            moder = lvls[lvl]
            chosen = False

          # Checking Secret Code for Hell Mode
          if event.direction == secretkey[seecount]:
            seecount += 1
          else:
            seecount = 0

          breakout = False
          break

    # Activaction for Hell mode
    if seecount == 8:
      mixer.music.load(filepather('sound/hazard.mp3'))     # Hell Mode Start Music
      mixer.music.play()
      blink_screen(warning,3)        # Blink Warning Image 3 times
      sense.load_image(filepather(hell_mode['pic']),redraw=True)  # Hell Mode Image
      time.sleep(1)
      moder = hell_mode
      mixer.music.stop()             # Stop and Unload Music
      mixer.music.unload()
      break

    # Update Diffifculty level Chosen
    if chooselvl < 0:
      chooselvl = 1
    elif chooselvl > 1:
      chooselvl = 0

  gamelist = [race, snake, maze, shooter, ballblaster, reaction] # List of Games in Hachi-Bit Archive
  # Randomise the order of games after choosing Diff
  for _ in range(len(gamelist)):
    countdown()             # Misc Function
    gamer = random.choice(gamelist)
    gamelist.remove(gamer)
    # setup to get result from function
    result = gamer(moder)
    preexitprogram()        # Misc Function

    # Output for Losing a Game
    if result == 'gameover':
      preexitprogram()     # Misc Function
      mixer.music.load(filepather('sound/gameoveryea.mp3'))    # Gameover Music
      mixer.music.play()
      time.sleep(1)
      # Images for Gameover
      sense.load_image(filepather('gameover/1.png'),redraw=True)
      time.sleep(1)
      sense.load_image(filepather('gameover/2.png'),redraw=True)
      time.sleep(1)
      sense.load_image(filepather('gameover/3.png'),redraw=True)
      time.sleep(6)
      main()

    # Output for winning a game
    elif result == 'win':
      mixer.music.load(filepather('sound/leveldone.mp3'))      # Win music
      mixer.music.play()
      sense.load_image(filepather('medal.png'),redraw=True)    # Image for Win
      time.sleep(7)

  # Output for winning All 6 Games
  mixer.music.load(filepather('sound/thankyou.mp3'))      # Win All Music
  mixer.music.play()
  sense.load_image(filepather('trophy.png'),redraw=True)  # Win All Image
  time.sleep(5)

  # Restart Program
  preexitprogram()  # Restore Function
  main()            # Main Function

# main loop
if __name__ == "__main__":
  main()
