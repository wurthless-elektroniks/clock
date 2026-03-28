'''
PwmU16BrightnessController

Kept separate from pwmbrightnessctrl.py as it occupies more memory.
'''

import math
from machine import Pin,PWM
from wurthless.clock.common.brightness import BRIGHTNESS_MAXIMUM_VALUE, BRIGHTNESS_MINIMUM_VALUE, clamp_brightness

class PwmU16BrightnessController():
    def __init__(self, brightness_pin_id: int, strobe_frequency: int, half_brightness: bool = False):
        self._half_brightness = half_brightness
        self._brightness_pwm = PWM(Pin(brightness_pin_id))
        self._strobe_frequency = strobe_frequency
        self.setBrightness(BRIGHTNESS_MAXIMUM_VALUE)

    def setBrightness(self, brightness):
        brightness_inverse = (BRIGHTNESS_MAXIMUM_VALUE - brightness) + BRIGHTNESS_MINIMUM_VALUE
        duty = int(65535 * (1.0 - math.log(brightness_inverse, BRIGHTNESS_MAXIMUM_VALUE+1)) )
        
        if self._half_brightness:
            duty >>= 1

        self._brightness_pwm.freq(self._strobe_frequency * 2)
        self._brightness_pwm.duty_u16(duty)

    def deinit(self):
        self._brightness_pwm.deinit()
