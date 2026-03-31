#
# Prompt code for manual inputs
# Moved out of clockmain.py and cleaned up
#

from wurthless.clock.api.display import DISPLAY_TYPE_NUMERIC, DISPLAY_TYPE_SEVEN_SEGMENT
from wurthless.clock.common.bcd import unpackBcd
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits
from wurthless.clock.common.timestamp import autoformatHourIn12HourTime
from wurthless.clock.common.brightness import BRIGHTNESS_MAXIMUM_VALUE, BRIGHTNESS_MINIMUM_VALUE, BRIGHTNESS_TOTAL_STEPS, decrement_brightness
from wurthless.clock.common.messages import messagesDisplaySure, messagesDisplayYes, messagesDisplayNo

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
            self.display.setBrightness( BRIGHTNESS_MAXIMUM_VALUE if self.even_odd else BRIGHTNESS_MINIMUM_VALUE )
            self.even_odd = not self.even_odd
            self.counter = self.flash_ticks

    def reset(self):
        self.flash_ticks = DELAY_TICKS
        self.counter = self.flash_ticks
        self.even_odd = True  # even = fullbrite, odd = lowbrite
        self.display.setBrightness(BRIGHTNESS_MAXIMUM_VALUE)

def clamp(val: int, minval: int, maxval: int) -> int:
    inp = val
    if inp < minval:
        inp = maxval
    elif inp > maxval:
        inp = minval
    return inp

def promptFourDigit(tot, inputs, valin: int, minval: int=0, maxval: int=9999):
    inp = clamp(valin, minval, maxval)
    display = tot.display()
    flasher = DisplayFlasher(display)
    
    def _rerender():
        bcd = unpackBcd(inp / 100, inp % 100)
        display.setDigitsNumeric( bcd[0], bcd[1], bcd[2], bcd[3] )

    _rerender()
    while True:
        if inputs.strobe() is False:
            flasher.tick()
            snooze()
        elif inputs.up():
            inp = clamp(inp + 1, minval, maxval)
            flasher.reset()
            _rerender()
        elif inputs.down():
            inp = clamp(inp - 1, minval, maxval)
            flasher.reset()
            _rerender()
        elif inputs.set():
            return inp
        else:
            pass

def promptTwoDigit(tot, inputs, valin, minval=0, maxval=99):
    inp = clamp(valin, minval, maxval)
    display = tot.display()
    flasher = DisplayFlasher(display)

    def _rerender():
        bcd = unpackBcd(0, inp)
        display.setDigitsNumeric( None, None, bcd[2], bcd[3]  )

    _rerender()
    while True:
        if inputs.strobe() is False:
            flasher.tick()
            snooze()
        elif inputs.up():
            inp = clamp(inp + 1, minval, maxval)
            flasher.reset()
            _rerender()
        elif inputs.down():
            inp = clamp(inp - 1, minval, maxval)
            flasher.reset()
            _rerender()
        elif inputs.set():
            return inp
        else:
            pass

def promptYear(tot, inputs, year):
    return promptFourDigit(tot, inputs, year, minval=2022, maxval=2099)

def promptMonthOrDay(tot, inputs, valin, maxval):
    return promptTwoDigit(tot, inputs, valin, minval=1, maxval=maxval)

########################################################################################################################

def promptTime(tot, inputs, hour, minute):
    display = tot.display()
    flasher = DisplayFlasher(display)

    retval = [ 0, 0 ]

    inp = hour

    def _rerenderHour():
        hour_visible = autoformatHourIn12HourTime(tot, inp)
        bcd = unpackBcd(inp, 0)
        tot.display().setDigitsNumeric( bcd[0], bcd[1], None, None )
    
    _rerenderHour()
    
    while True:
        if inputs.strobe() is False:
            flasher.tick()
            snooze()
        if inputs.up():
            inp = clamp(inp + 1, minval=0, maxval=23)
            flasher.reset()
            _rerenderHour()
        elif inputs.down():
            inp = clamp(inp - 1, minval=0, maxval=23)
            flasher.reset()
            _rerenderHour()
        elif inputs.set():
            retval[0] = inp
            break
        else:
            pass

    flasher.reset()

    def _rerenderMinute():
        hour_visible = autoformatHourIn12HourTime(tot, retval[0])
        bcd = unpackBcd(retval[0], inp)
        tot.display().setDigitsNumeric( bcd[0], bcd[1], bcd[2], bcd[3] )

    inp = minute
    _rerenderMinute()
    while True:
        if inputs.strobe() is False:
            flasher.tick()
            snooze()
        if inputs.up():
            inp = clamp(inp + 1, minval=0, maxval=59)
            flasher.reset()
            _rerenderMinute()
        elif inputs.down():
            inp = clamp(inp - 1, minval=0, maxval=59)
            flasher.reset()
            _rerenderMinute()
        elif inputs.set():
            retval[1] = inp
            return retval
        else:
            pass

def promptDst(tot,inputs,dst):
    flash_state = False
    display_delay_ticks = 0
    inp = dst

    display_type = tot.display().getDisplayType()

    tot.display().setBrightness(BRIGHTNESS_MAXIMUM_VALUE)
    while True:
        if display_delay_ticks == 0:
            display_delay_ticks = DELAY_TICKS

            if display_type == DISPLAY_TYPE_SEVEN_SEGMENT:
                if flash_state is False:
                    # "dST"
                    tot.display().setDigitsBinary(0b00000000, 0b01011110, 0b01101101, 0b01111000)
                else:
                    # either "oFF" or "on"
                    if inp is True:
                        tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01010100, 0b00000000)
                    else:
                        tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01110001, 0b01110001)
            elif display_type == DISPLAY_TYPE_NUMERIC:
                tot.display().setDigitsNumeric(
                    6, 5, 7, 1 if inp is True else 0
                )
                tot.display().setBrightness(BRIGHTNESS_MAXIMUM_VALUE if flash_state else BRIGHTNESS_MINIMUM_VALUE)

        else:
            display_delay_ticks -= 1

        if inputs.strobe() is False:
            flash_state = not flash_state
        elif inputs.up() or inputs.down():
            inp = not inp
            flash_state = False
            display_delay_ticks = 0
        elif inputs.set():
            return inp
        else:
            pass
        snooze()

def promptConfirm(direct_inputs, display) -> bool:
    brightness = BRIGHTNESS_MAXIMUM_VALUE
    display.setBrightness(brightness)
    messagesDisplaySure(display)
    try:
        sleep_step = 3.0 / BRIGHTNESS_TOTAL_STEPS
        for _ in range(BRIGHTNESS_TOTAL_STEPS):
            # if user releases SET, cancel
            direct_inputs.strobe()
            if direct_inputs.set() is False:
                return False
            
            brightness = decrement_brightness(brightness)
            display.setBrightness(brightness)

            time.sleep(sleep_step)
        return True
    finally:
        # max out brightness on the way out
        display.setBrightness(BRIGHTNESS_MAXIMUM_VALUE)


def promptMenu(display,
               inputs,
               items,
               default_selection=None) -> int:
    '''
    Builds a simple menu and displays it.

    items is a list of callbacks accepting a Display as the parameter, intended to point at
    one of the many functions in messages.py. The function will return the index of the selection;
    it's up to the caller to act on it. If None is encountered, the item will be skipped over.
    '''

    max_selection = len(items) - 1
    selection = 0 if default_selection is None else clamp(default_selection, 0, max_selection)

    flasher = DisplayFlasher(display)

    while True:
        display.setBrightness(BRIGHTNESS_MAXIMUM_VALUE)
        print(f"display idx: {selection}")
        items[selection](display)
        flasher.reset()

        while True:
            if inputs.strobe() is False:
                flasher.tick()
                snooze()
            elif inputs.up():
                while True:
                    selection = clamp(selection + 1, 0, max_selection)
                    if items[selection] is not None:
                        break
                break
            elif inputs.down():
                while True:
                    selection = clamp(selection - 1, 0, max_selection)
                    if items[selection] is not None:
                        break
                break
            elif inputs.set():
                return selection


def promptBoolean(display,
                  inputs,
                  message_false = messagesDisplayNo,
                  message_true = messagesDisplayYes,
                  default_selection = False) -> bool:
    items = [
        message_false,
        message_true
    ]
    return promptMenu(display, inputs, items, default_selection=1 if default_selection else 0) == 1
