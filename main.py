# Imports used
from adafruit_crickit import crickit
from subprocess import Popen
import os
import signal
import time
import pathlib

# initialise crickit hat ports
ss = crickit.seesaw
ragebutton = crickit.SIGNAL1

# init button port
ss.pin_mode(ragebutton, ss.INPUT_PULLUP)

if __name__ == "__main__": # check if program running
  while True:
    gameproc = Popen(['python3', f'{pathlib.Path(__file__).parent}/game.py']) # runs the main program game
    gamepid = gameproc.pid # grabs specific game PID to kill the specific game later on

    # check if Pushbutton is pressed for 2 Secs
    while True:
      time.sleep(1)
      if not ss.digital_read(ragebutton):
        count += 1
      else:
        count = 0

      # Output when pushbutton is pressed for 2 secs
      if count == 2:
        os.kill(gamepid,signal.SIGKILL) # kill the game
        break

    #restarts program
