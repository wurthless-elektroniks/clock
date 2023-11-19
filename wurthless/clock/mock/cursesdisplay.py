#
# Curses-based display when clock is in mock mode
#

import curses
from curses import wrapper
from time import sleep

from wurthless.clock.api.display import Display
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits

LITE = u'\u2591' 
DARK = u'\u2592'

def appendCharTab(bits, chars, tab):
    for i in range(0,7):
        bit = (bits >> i) & 1
        tab[chars[i]] = LITE if bit == 1 else DARK

def updateScreen(stdscr,a,b,c,d):
    screenstr = u"""
     aaaa   hhhh   oooo    vvvv
    f    b m    i t    p  0    w
    f    b m    i t    p  0    w
     gggg   nnnn   uuuu    1111
    e    c l    j s    q  z    x
    e    c l    j s    q  z    x
     dddd   kkkk   rrrr    yyyy
    """

    chartab = {}
    appendCharTab(a, ['a','b','c','d','e','f','g'], chartab)
    appendCharTab(b, ['h','i','j','k','l','m','n'], chartab)
    appendCharTab(c, ['o','p','q','r','s','t','u'], chartab)
    appendCharTab(d, ['v','w','x','y','z','0','1'], chartab)

    x = 0
    y = 0
    
    for c in screenstr:
        if c == ' ':
            x += 1
            continue
        elif c == '\n':
            y += 1
            x = 0
        elif c == '\r':
            x = 0
        else:
           stdscr.addch(y,x,chartab[c],curses.A_DIM if chartab[c] == DARK else curses.A_NORMAL)
           x += 1

class CursesDisplay(Display):
    def __init__(self, scr):
        self.scr = scr

    def setBrightness(self, brightness):
        pass

    def setDigitsBinary(self,a,b,c,d):
        updateScreen(self.scr,a,b,c,d)
        self.scr.refresh()

