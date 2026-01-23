'''
Display driven off shift registers (74HC595)
'''

from machine import Pin, PWM

from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.common.sn74hc595 import sn74hc595_shift_bits_out

registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_latch_pin",
             "Int",
             "Shift register(s) latch pin (latches shift register contents to outputs)",
             15)

registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "shiftreg_reset_pin",
             "Int",
             "Shift register reset pin (active low; clears shift register contents)",
             14)

registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_clock_pin",
             "Int",
             "Serial clock pin (data pin is shifted in on rising edge)",
             13)

registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "serial_data_pin",
             "Int",
             "Serial data pin",
             12)

registerCvar("wurthless.clock.drivers.display.shiftydisplay",
             "brightness_pwm_pin",
             "Int",
             "PWM pin",
             10)

# brightness table as frequency/duty cycle.
# you might need to change these if there is no resistor in-line with the master output transistor's base,
# or else you run the risk of frying the LEDs.
# these assume that there's a resistor in-line or that the LEDs can tolerate 3v3 directly.
# in my own experience it's fine to use a 2k resistor on the base of the master (brightness) transistor
# and not do a whole lot else.
DEFAULT_BRIGHTNESS_TABLE = [
    [ 2000, int(65535 * (3/10)) ],
    [ 2000, int(65535 * (4/10)) ],
    [ 2000, int(65535 * (5/10)) ],
    [ 2000, int(65535 * (6/10)) ],
    [ 2000, int(65535 * (7/10)) ],
    [ 2000, int(65535 * (8/10)) ],
    [ 2000, int(65535 * (9/10)) ],
    [ 2000, int(65535 * (10/10)) ]
]

class ShiftyDisplay(SevenSegmentDisplay):
    def __init__(self, tot):

        serial_data_pin_id     = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "serial_data_pin")
        serial_clock_pin_id    = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "serial_clock_pin")
        shiftreg_reset_pin_id  = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "shiftreg_reset_pin")
        shiftreg_latch_pin_id  = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "shiftreg_latch_pin")

        brightness_pwm_pin     = tot.cvars().get("wurthless.clock.drivers.display.shiftydisplay", "brightness_pwm_pin")

        self._serial_data_pin    = Pin(serial_data_pin_id, Pin.OUT)
        self._serial_clock_pin   = Pin(serial_clock_pin_id, Pin.OUT)
        self._shiftreg_reset_pin = Pin(shiftreg_reset_pin_id, Pin.OUT)
        self._shiftreg_latch_pin = Pin(shiftreg_latch_pin_id, Pin.OUT)

        self.brightness_pwm = PWM(Pin(brightness_pwm_pin, Pin.OUT))

        # bring up display but in blank state.
        self.setBrightness(8)
        self.blank()

    def setBrightnessPwmRaw(self, freq, duty):
        self.brightness_pwm.freq(freq)
        self.brightness_pwm.duty_u16(duty)

    def setBrightness(self, brightness):
        if brightness < 1:
            brightness = 1
        if brightness > 8:
            brightness = 8

        brightness -= 1
        self.setBrightnessPwmRaw( DEFAULT_BRIGHTNESS_TABLE[brightness][0], DEFAULT_BRIGHTNESS_TABLE[brightness][1] )

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

