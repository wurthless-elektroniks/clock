'''
Display driven off shift registers (74HC595)
'''

from machine import Pin, PWM

from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.common.sn74hc595 import sn74hc595_shift_bits_out


# Shift register(s) latch pin (latches shift register contents to outputs)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_latch_pin",
             "Int",
             15)

# Shift register reset pin (active low; clears shift register contents)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_reset_pin",
             "Int",
             14)

# Serial clock pin (data pin is shifted in on rising edge)
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_clock_pin",
             "Int",
             13)

# Serial data pin
registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_data_pin",
             "Int",
             12)

class ShiftyDisplay(SevenSegmentDisplay):
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

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        sn74hc595_shift_bits_out(32,
                                 d | c << 8 | b << 16 | a << 24,
                                 self._serial_data_pin,
                                 self._serial_clock_pin,
                                 self._shiftreg_reset_pin,
                                 self._shiftreg_latch_pin)
