'''
Display device with colon attached, which is controlled by PWM.
'''

from machine import Pin, PWM, Timer
from wurthless.clock.api.display import COLON_STATE_BLINK, COLON_STATE_OFF, COLON_STATE_ON, Display
from wurthless.clock.drivers.display.decorateddisplay import DecoratedDisplay

class ColonGpioDisplay(DecoratedDisplay):
    def __init__(self, parent, gpio_pin):
        super().__init__(parent)
        self._gpio_pin = gpio_pin
        self._gpio = Pin(self._gpio_pin, Pin.OUT)
        self._colon_state = 0
        self.setColonState(COLON_STATE_OFF)

        self._colon_led_state = 0
        self._timer = Timer(-1, freq = 2, callback = lambda t: self._tick())

    def _tick(self):
        if self._colon_state == COLON_STATE_BLINK:
            led_state = 1 if self._colon_led_state == 0 else 0
            self._gpio.value(led_state)
            self._colon_led_state = led_state

    def setColonState(self, colon_state):
        # bit dangerous due to no mutex use but whatever
        led_state = 0 if colon_state == COLON_STATE_OFF else 1
        self._gpio.value(led_state)
        self._colon_led_state = led_state
        self._colon_state = colon_state

