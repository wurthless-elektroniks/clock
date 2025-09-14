'''
Display with two SN74HC373s driving four CD4028 chips, or similar configuration
Used with first version of the Nixie driver circuit
'''

import time
from machine import Pin, PWM
from wurthless.clock.api.display import Display,DisplayType
from wurthless.clock.cvars.cvars import registerCvar

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"latchenable_dig01_pin",
             u"Int",
             u"Latch enable for digits 0/1",
             13)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"latchenable_dig23_pin",
             u"Int",
             u"Latch enable for digits 2/3",
             14)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig02_bit_0_pin",
             u"Int",
             u"Output for digit 0/2 BCD bit 0",
             15)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig02_bit_1_pin",
             u"Int",
             u"Output for digit 0/2 BCD bit 1",
             16)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig02_bit_2_pin",
             u"Int",
             u"Output for digit 0/2 BCD bit 2",
             17)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig02_bit_3_pin",
             u"Int",
             u"Output for digit 0/2 BCD bit 3",
             18)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig13_bit_0_pin",
             u"Int",
             u"Output for digit 1/3 BCD bit 0",
             19)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig13_bit_1_pin",
             u"Int",
             u"Output for digit 1/3 BCD bit 1",
             20)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig13_bit_2_pin",
             u"Int",
             u"Output for digit 1/3 BCD bit 2",
             21)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"dig13_bit_3_pin",
             u"Int",
             u"Output for digit 1/3 BCD bit 3",
             22)

registerCvar(u"wurthless.clock.drivers.display.bcdlatchdisplay",
             u"brightness_pwm_pin",
             u"Int",
             u"PWM pin for controlling brightness.",
             10)

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

class BcdLatchDisplay(Display):
    def __init__(self, tot):
        cvars = tot.cvars()

        latchenable_dig01_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "latchenable_dig01_pin" )
        latchenable_dig23_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "latchenable_dig23_pin" )

        dig02_bit_0_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig02_bit_0_pin" )
        dig02_bit_1_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig02_bit_1_pin" )
        dig02_bit_2_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig02_bit_2_pin" )
        dig02_bit_3_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig02_bit_3_pin" )
        dig13_bit_0_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig13_bit_0_pin" )
        dig13_bit_1_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig13_bit_1_pin" )
        dig13_bit_2_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig13_bit_2_pin" )
        dig13_bit_3_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "dig13_bit_3_pin" )

        brightness_pwm_pin = cvars.get("wurthless.clock.drivers.display.bcdlatchdisplay", "brightness_pwm_pin")

        self._digit_output_pins = []
        for pin in [ dig02_bit_0_pin, dig02_bit_1_pin, dig02_bit_2_pin, dig02_bit_3_pin, \
                     dig13_bit_0_pin, dig13_bit_1_pin, dig13_bit_2_pin, dig13_bit_3_pin ]:
            pin_obj = Pin(pin, Pin.OUT)
            self._digit_output_pins.append(pin_obj)

        self._latchenable_dig01_pin = Pin(latchenable_dig01_pin, Pin.OUT)
        self._latchenable_dig23_pin = Pin(latchenable_dig23_pin, Pin.OUT)

        self._brightness_pwm = PWM(Pin(brightness_pwm_pin, Pin.OUT))
        self.setBrightness(8)
        self.setDigitsNumeric(None, None, None, None)

    def getDisplayType(self):
        return DisplayType.NUMERIC
    
    def setBrightnessPwmRaw(self, freq, duty):
        self._brightness_pwm.freq(freq)
        self._brightness_pwm.duty_u16(duty)

    def setBrightness(self, brightness):
        if brightness < 1:
            brightness = 1
        if brightness > 8:
            brightness = 8

        brightness -= 1
        self.setBrightnessPwmRaw( DEFAULT_BRIGHTNESS_TABLE[brightness][0], DEFAULT_BRIGHTNESS_TABLE[brightness][1] )

    def _latchDigits(self, dig0, dig1):
        output_byte = (dig1 << 4) | dig0
        bitmasks = [ 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80 ]
        for i, bitmask in enumerate(bitmasks):
            self._digit_output_pins[i].value( (output_byte & bitmask) != 0)

    def setDigitsNumeric(self, a, b, c, d):
        digits_out = [ 0xF, 0xF, 0xF, 0xF ]

        if a is not None and 0 <= a <= 9:
            digits_out[0] = a
    
        if b is not None and 0 <= b <= 9:
            digits_out[1] = b
        
        if c is not None and 0 <= c <= 9:
            digits_out[2] = c

        if d is not None and 0 <= d <= 9:
            digits_out[3] = d

        self._latchDigits(digits_out[0], digits_out[1])
        self._latchenable_dig01_pin.value(1)
        time.sleep(0.001)
        self._latchenable_dig01_pin.value(0)
        self._latchDigits(digits_out[2], digits_out[3])
        self._latchenable_dig23_pin.value(1)
        time.sleep(0.001)
        self._latchenable_dig23_pin.value(0)
