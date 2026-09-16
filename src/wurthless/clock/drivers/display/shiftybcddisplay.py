'''
Two shift registers (74HC595) driving four CD4028 4-to-10 demuxers
More modern version of the Nixie display driver

Needs serious cleanup, have to do that later
'''

import time
from machine import Pin, PWM

from wurthless.clock.api.display import Display,DISPLAY_TYPE_NUMERIC
from wurthless.clock.cvars.cvars import registerCvar

# Shift register(s) latch pin (latches shift register contents to outputs)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_latch_pin",
             "Int",
             15)

# Shift register reset pin (active low; clears shift register contents)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_reset_pin",
             "Int",
             13)

# Serial clock pin (data pin is shifted in on rising edge)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_clock_pin",
             "Int",
             14)

# Serial data pin
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_data_pin",
             "Int",
             12)


lut = [
    8,
    6,
    5,
    9,
    7,
    0,
    2,
    4,
    1,
    3
]

class ShiftyBcdDisplay(Display):
    def __init__(self, tot):

        serial_data_pin_id     = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "serial_data_pin")
        serial_clock_pin_id    = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "serial_clock_pin")
        shiftreg_reset_pin_id  = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "shiftreg_reset_pin")
        shiftreg_latch_pin_id  = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "shiftreg_latch_pin")

        self._serial_data_pin    = Pin(serial_data_pin_id, Pin.OUT)
        self._serial_clock_pin   = Pin(serial_clock_pin_id, Pin.OUT)
        self._shiftreg_reset_pin = Pin(shiftreg_reset_pin_id, Pin.OUT)
        self._shiftreg_latch_pin = Pin(shiftreg_latch_pin_id, Pin.OUT)

        # bring up display but in blank state.
        self.blank()


    def shift_bits_out_l_to_r(self, bits):
        for i in range(0,4):
            self._serial_data_pin.value( (bits & (1 << 3-i)) != 0 )
            self._serial_clock_pin.value(1)
            self._serial_clock_pin.value(0)

    def shift_bits_out_r_to_l(self, bits):
        for i in range(0,4):
            self._serial_data_pin.value( (bits & (1 << i)) != 0 )
            self._serial_clock_pin.value(1)
            self._serial_clock_pin.value(0)

    
    def getDisplayType(self):
        return DISPLAY_TYPE_NUMERIC

    def setDigitsNumeric(self, a, b, c, d):
        digits_out = [ 0xF, 0xF, 0xF, 0xF ]

        if a is not None and 0 <= a <= 9:
            digits_out[0] = lut[a]
    
        if b is not None and 0 <= b <= 9:
            digits_out[1] = lut[b]
        
        if c is not None and 0 <= c <= 9:
            digits_out[2] = lut[c]

        if d is not None and 0 <= d <= 9:
            digits_out[3] = lut[d]


        self._shiftreg_reset_pin.value(0)
        self._serial_data_pin.value(0)
        self._serial_clock_pin.value(0)
        self._shiftreg_latch_pin.value(0)
        self._shiftreg_reset_pin.value(1)

        # bits have to be shifted out in this order.
        # digit order can be whatever you want
        self.shift_bits_out_r_to_l(digits_out[3])
        self.shift_bits_out_l_to_r(digits_out[2])
        self.shift_bits_out_r_to_l(digits_out[1])
        self.shift_bits_out_l_to_r(digits_out[0])

        self._shiftreg_latch_pin.value(1)
        self._shiftreg_latch_pin.value(1)
        self._shiftreg_latch_pin.value(0)
