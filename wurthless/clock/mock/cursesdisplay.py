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

class CursesDisplay(Display):
    def __init__(self, scr):
        self.scr = scr
        self.brightness = 8
        self.dig_a = 0
        self.dig_b = 0
        self.dig_c = 0
        self.dig_d = 0

    def _refresh(self):
        screenstr = u"""
             aaaa   hhhh   oooo    vvvv
            f    b m    i t    p  0    w
            f    b m    i t    p  0    w
             gggg   nnnn   uuuu    1111
            e    c l    j s    q  z    x
            e    c l    j s    q  z    x
             dddd   kkkk   rrrr    yyyy
            """

        self.scr.clear()
        chartab = {}
        appendCharTab(self.dig_a, ['a','b','c','d','e','f','g'], chartab)
        appendCharTab(self.dig_b, ['h','i','j','k','l','m','n'], chartab)
        appendCharTab(self.dig_c, ['o','p','q','r','s','t','u'], chartab)
        appendCharTab(self.dig_d, ['v','w','x','y','z','0','1'], chartab)

        color_tab = [ 0,
                    curses.color_pair(1),
                    curses.color_pair(2),
                    curses.color_pair(3),
                    curses.color_pair(4),
                    curses.color_pair(5),
                    curses.color_pair(6),
                    curses.color_pair(7),
                    curses.color_pair(8),
                    ]
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
                self.scr.addch(y,x,chartab[c], (curses.A_DIM if chartab[c] == DARK else (curses.A_NORMAL|color_tab[self.brightness])) )
            x += 1

        self.scr.refresh()

    def setBrightness(self, brightness):
        self.brightness = brightness
        self._refresh()

    def setDigitsBinary(self,a,b,c,d):
        self.dig_a = a
        self.dig_b = b
        self.dig_c = c
        self.dig_d = d
        self._refresh()


