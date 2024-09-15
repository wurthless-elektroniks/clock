#
# Input interface for curses.
#

import curses

from threading import Thread,Lock
from wurthless.clock.api.inputs import Inputs

UP_BUTTON   = curses.KEY_UP
DOWN_BUTTON = curses.KEY_DOWN
SET_BUTTON  = curses.KEY_LEFT
DST_BUTTON  = curses.KEY_RIGHT

ALL_BUTTONS = [ UP_BUTTON,DOWN_BUTTON,SET_BUTTON,DST_BUTTON ]

def _pollThreadThunk(obj):
    obj._pollThread()

class CursesInputs(Inputs):
    def __init__(self, scr):
        self.scr = scr
        self.mutex = Lock()
        self.inputs = {}
        self.strobe_inputs = {}

        for i in ALL_BUTTONS:
            self.inputs[i] = False
            self.strobe_inputs[i] = False

        self._pollThreadInst = Thread(target = _pollThreadThunk, args = [self])
        self._pollThreadInst.start()

    def _pollThread(self):
        print(u"pollthread started.")
        # keep polling for inputs and make a note of any keypress events on UP/DOWN/SET/DST
        while True:
            with self.mutex:
                chr = self.scr.getch()
                for i in ALL_BUTTONS:
                    if chr == i:
                        self.inputs[i] = True

    def strobe(self):
        # lock any and all inputs pressed between the last time we polled and now
        with self.mutex:
            for i in ALL_BUTTONS:
                self.strobe_inputs[i] = self.inputs[i]
                self.inputs[i] = False

        # this is running on PC, CPU time is not that critical.
        return self.up() or self.down() or self.set() or self.dst()

    def up(self):
        return self.strobe_inputs[UP_BUTTON] is True
    
    def down(self):
        return self.strobe_inputs[DOWN_BUTTON] is True
    
    def set(self):
        return self.strobe_inputs[SET_BUTTON] is True

    def dst(self):
        return self.strobe_inputs[DST_BUTTON] is True
