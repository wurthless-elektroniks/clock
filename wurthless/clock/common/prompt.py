#
# Prompt code for manual inputs
# Moved out of clockmain.py and cleaned up
#

from wurthless.clock.common.bcd import unpackBcd
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits
from wurthless.clock.common.timestamp import autoformatHourIn12HourTime

import time

try:
    from utime import sleep_ms
except:
    sleep_ms = lambda a : time.sleep(a / 1000)

TICK_TIME_MS = 10
snooze = lambda : sleep_ms(TICK_TIME_MS)

DELAY_TICKS = 20

class DisplayFlasher:
    def __init__(self, display):
        self.display = display
        self.reset()

    def tick(self):
        self.counter -= 1
        if self.counter == 0:
            self.display.setBrightness( 8 if self.even_odd else 2 )
            self.even_odd = not self.even_odd
            self.counter = self.flash_ticks

    def reset(self):
        self.flash_ticks = DELAY_TICKS
        self.counter = self.flash_ticks
        self.even_odd = True  # even = fullbrite, odd = lowbrite
        self.display.setBrightness(8)

def clamp(val, minval, maxval):
    inp = val
    if inp < minval:
        inp = maxval
    elif inp > maxval:
        inp = minval
    return inp

def promptFourDigit(tot, inputs, valin, minval=0, maxval=9999):
    inp = clamp(valin, minval, maxval)
    display = tot.display()
    flasher = DisplayFlasher(display)
    
    while True:
        bcd = unpackBcd(inp / 100, inp % 100)
        digs = sevensegNumbersToDigits( bcd[0], bcd[1], bcd[2], bcd[3] )
        display.setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        inputs.strobe()
        if inputs.up():
            inp = clamp(inp + 1, minval, maxval)
            flasher.reset()
        elif inputs.down():
            inp = clamp(inp - 1, minval, maxval)
            flasher.reset()
        elif inputs.set():
            return inp
        else:
            flasher.tick()
            snooze()

def promptTwoDigit(tot, inputs, valin, minval=0, maxval=99):
    inp = clamp(valin, minval, maxval)
    display = tot.display()
    flasher = DisplayFlasher(display)

    while True:
        bcd = unpackBcd(0, inp)
        digs = sevensegNumbersToDigits( None, None, bcd[2], bcd[3]  )
        display.setDigitsBinary( 0, 0, digs[2], digs[3] )
        inputs.strobe()
        if inputs.up():
            inp = clamp(inp + 1, minval, maxval)
            flasher.reset()
        elif inputs.down():
            inp = clamp(inp - 1, minval, maxval)
            flasher.reset()
        elif inputs.set():
            return inp
        else:
            flasher.tick()
            snooze()

def promptYear(tot, inputs, year):
    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr") is True
    if use_12hr:
        return 2000 + promptTwoDigit(tot, inputs, year - 2000, minval=22, maxval=99)
    else:
        return promptFourDigit(tot, inputs, year, minval=2022, maxval=2099)

def promptMonthOrDay(tot, inputs, valin, maxval):
    return promptTwoDigit(tot, inputs, valin, minval=1, maxval=maxval)

########################################################################################################################

def promptTime(tot, inputs, hour, minute):
    display = tot.display()
    flasher = DisplayFlasher(display)

    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr") is True

    retval = [ 0, 0 ]

    inp = hour

    while True:
        hour_visible = autoformatHourIn12HourTime(tot, inp)
        bcd = unpackBcd(inp, 0)
        digs = sevensegNumbersToDigits( bcd[0], bcd[1], None, None )

        # set segment A to indicate pm in 12-hour mode
        if use_12hr and hour_visible[1] is True:
            digs[0] |= 1

        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )

        inputs.strobe()
        if inputs.up():
            inp = clamp(inp + 1, minval=0, maxval=23)
            flasher.reset()
        elif inputs.down():
            inp = clamp(inp - 1, minval=0, maxval=23)
            flasher.reset()
        elif inputs.set():
            retval[0] = inp
            break
        else:
            flasher.tick()
            snooze()

    flasher.reset()

    inp = minute
    while True:
        hour_visible = autoformatHourIn12HourTime(tot, retval[0])
        bcd = unpackBcd(retval[0], inp)
        digs = sevensegNumbersToDigits( bcd[0], bcd[1], bcd[2], bcd[3] )

        # set segment A to indicate pm in 12-hour mode
        if use_12hr and hour_visible[1] is True:
            digs[0] |= 1

        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )

        inputs.strobe()
        if inputs.up():
            inp = clamp(inp + 1, minval=0, maxval=59)
            flasher.reset()
        elif inputs.down():
            inp = clamp(inp - 1, minval=0, maxval=59)
            flasher.reset()
        elif inputs.set():
            retval[1] = inp
            return retval
        else:
            flasher.tick()
            snooze()

def promptDst(tot,inputs,dst):
    flash_state = False
    display_delay_ticks = 0
    inp = dst
    while True:
        if display_delay_ticks == 0:
            display_delay_ticks = DELAY_TICKS
            if flash_state is False:
                # "dST"
                tot.display().setDigitsBinary+-(0b00000000, 0b01011110, 0b01101101, 0b01111000)
            else: 
                # either "oFF" or "on"
                if inp is True:
                    tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01010100, 0b00000000)
                else:
                    tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01110001, 0b01110001)
        else:
            display_delay_ticks -= 1

        inputs.strobe()
        if inputs.up() or inputs.down():
            inp = not inp
            flash_state = False
            display_delay_ticks = 0
        elif inputs.set():
            return inp
        else:
            flash_state = not flash_state
        snooze()