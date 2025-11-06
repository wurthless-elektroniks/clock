'''
Display device with colon attached, which is controlled by PWM.
'''

from machine import Pin, PWM
from wurthless.clock.api.display import COLON_STATE_BLINK, COLON_STATE_OFF, COLON_STATE_ON, Display
from wurthless.clock.drivers.display.decorateddisplay import DecoratedDisplay

class ColonGpioDisplay(DecoratedDisplay):
    def __init__(self, parent, gpio_pin):
        super().__init__(parent)
        self._gpio_pin = gpio_pin
        self._gpio = None
        self._gpio_pwm = None
        self.setColonState(COLON_STATE_OFF)

    def _reinit_input(self):
        if self._gpio_pwm is not None:
            self._gpio_pwm.deinit()
            self._gpio_pwm = None
        self._gpio = Pin(self._gpio_pin, Pin.OUT)

    def setColonState(self, colon_state):
        if colon_state == COLON_STATE_OFF:
            self._reinit_input()
            self._gpio.value(0)
        elif colon_state == COLON_STATE_ON:
            self._reinit_input()
            self._gpio.value(1)
        elif colon_state == COLON_STATE_BLINK:
            self._reinit_input()
            self._gpio_pwm = PWM(self._gpio)
            self._gpio_pwm.freq(2)
