'''
Display decorator that mixes in a PwmBrightnessController or PwmU16BrightnessController and allows
it to be controlled on `setBrightness()`.

Most display drivers have their own cvars for configuring which pin is used for brightness.
This is a holdover of an old idea where the runtime environment would be configured entirely
using .ini files instead of board-specific init files. This may be dropped in the future, as it's
an idea that never panned out. Legacy drivers will use the PwmBrightnessControllers directly for now.

'''

from wurthless.clock.drivers.display.decorateddisplay import DecoratedDisplay
from wurthless.clock.common.pwmbrightnessctrl import PwmBrightnessController
from wurthless.clock.common.pwmu16brightnessctrl import PwmU16BrightnessController

class PwmBrightnessDisplay(DecoratedDisplay):
    def __init__(self,
                 parent,
                 pwm_pin_id: int,
                 pwm_frequency:   int = 2000,
                 half_brightness: bool = False):
        super().__init__(parent)

        self._brightness_ctrl = PwmBrightnessController(pwm_pin_id,
                                                        pwm_frequency,
                                                        half_brightness=half_brightness)

    def setBrightness(self, brightness):
        self._brightness_ctrl.setBrightness(brightness)

class PwmU16BrightnessDisplay(DecoratedDisplay):
    def __init__(self,
                 parent,
                 pwm_pin_id: int,
                 pwm_frequency:   int = 2000,
                 half_brightness: bool = False):
        super().__init__(parent)

        self._brightness_ctrl = PwmU16BrightnessController(pwm_pin_id,
                                                           pwm_frequency,
                                                           half_brightness=half_brightness)

    def setBrightness(self, brightness):
        self._brightness_ctrl.setBrightness(brightness)
