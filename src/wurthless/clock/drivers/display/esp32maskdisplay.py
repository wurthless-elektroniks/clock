#
# Display driver that accesses the ESP32 GPIOs directly.
#

import sys
from micropython import const
from machine import Pin,Timer,mem32,disable_irq,enable_irq,PWM
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.api.display import Display
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay
from wurthless.clock.common.pwmbrightnessctrl import PwmBrightnessController

# i'm serious. we are accessing the hardware directly. it's too slow otherwise.
# DANGER! this I/O register changes depending on what ESP32 we are using.

if sys.implementation._machine.find("ESP32C3") >= 0:
    # for esp32c3, have to check implementation, platform will be esp32 and that's too ambiguous
    import wurthless.clock.drivers.machine.esp32c3 as esp32c3
    esp32c3.configureEsp32C3IoPins()
elif sys.platform == u'esp32':
    GPIO_OUT_REG = 0x3FF44004
else:
    print(u"DANGER: platform not recognized (%s). defaulting to default esp32 gpio register. you're entering very dangerous territory if you start execution."%(sys.platform))
    GPIO_OUT_REG = 0x3FF44004

# default pin assignments are for TMUCITW v8
# cvars are no longer used here because of their heavy memory usage
# and because TMUCITW v8 is the final LED revision (for now).
SEG_A_PIN = 4
SEG_B_PIN = 16
SEG_C_PIN = 5
SEG_D_PIN = 17
SEG_E_PIN = 18
SEG_F_PIN = 13
SEG_G_PIN = 27
DIGIT_0_PIN = 23
DIGIT_1_PIN = 19
DIGIT_2_PIN = 21
DIGIT_3_PIN = 22
BRIGHTNESS_PIN = 26

# Frequency at which we update the display
registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_frequency",
             u"Int",
             int((4*100)*4))

# If True, write directly to GPIO register without preserving other I/O settings. Default is False (off).
registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_fast",
             u"Boolean",
             False)

# If True, use half-brightness mode. Default is False (off).
registerCvar("wurthless.clock.drivers.display.esp32maskdisplay",
             "halfbright",
             "Boolean",
             False)

class Esp32MaskDisplay(SevenSegmentDisplay):
    def __init__(self, tot):
        cvars = tot.cvars()

        self.seg_pins = [ SEG_A_PIN, SEG_B_PIN, SEG_C_PIN, SEG_D_PIN, SEG_E_PIN, SEG_F_PIN, SEG_G_PIN ]
        self.dig_pins = [ DIGIT_0_PIN, DIGIT_1_PIN, DIGIT_2_PIN, DIGIT_3_PIN ]

        # force system to mark all pins as outputs
        for p in self.seg_pins+self.dig_pins:
            if sys.implementation._machine.find("ESP32C3") >= 0 and p in [18,19]:
                # we've already tried grabbing those, don't do it again or we'll get exceptions
                pass
            else:
                Pin(p,Pin.OUT).value(0)

        self.digs = [ 0b00000000, 0b00000000, 0b00000000, 0b00000000 ]
        
        # compute andmask
        andmask = 0
        for digit in range(0,4):
            andmask |= (1 << self.dig_pins[digit])
            for segment in range(0,7):
                andmask |= (1 << self.seg_pins[segment])
        self.andmask = ~andmask

        self.strobe_frequency = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_frequency")
        self.sm_state = 0
        self.sm_ptr = 0
        
        if cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_fast") is True:
            cb = self._strobe_fast
        else:
            cb = self._strobe
        
        self.timer = Timer(0, mode=Timer.PERIODIC, freq = self.strobe_frequency, callback=cb)

        pwm_pin = BRIGHTNESS_PIN
        halfbright = cvars.get("wurthless.clock.drivers.display.esp32maskdisplay", "halfbright")
        self._brightness_ctrl = PwmBrightnessController(pwm_pin, self.strobe_frequency, half_brightness=halfbright)

    def _strobe_fast(self, t):
        isr = disable_irq()
        mem32[GPIO_OUT_REG] = self.digs[self.sm_ptr]
        self.sm_ptr += 1
        self.sm_ptr &= 3
        enable_irq(isr)

    def _strobe(self,t):
        isr = disable_irq()
        mem32[GPIO_OUT_REG] = (mem32[GPIO_OUT_REG] & self.andmask) | self.digs[self.sm_ptr]
        self.sm_ptr += 1
        self.sm_ptr &= 3
        enable_irq(isr)

    def setBrightness(self, brightness):
        self._brightness_ctrl.setBrightness(brightness)

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 0x7F)
        b = int(b & 0x7F)
        c = int(c & 0x7F)
        d = int(d & 0x7F)
        
        # munge digits into raw i/os
        vals = [a,b,c,d]
        munged = [0,0,0,0]

        for digit in range(0,4):
            bits = vals[digit]
            v = (1 << self.dig_pins[digit])
            for segment in range(0,7):
                if ( bits & 1 ) == 1:
                    v |= (1 << self.seg_pins[segment])
                bits >>= 1
            munged[digit] = v

        isr = disable_irq()
        self.digs = munged
        enable_irq(isr)

    def shutdown(self):
        self.timer.deinit()
        self._brightness_ctrl.deinit()
        
        # disable all digit drives so the display goes blank
        isr = disable_irq()
        mem32[GPIO_OUT_REG] = (mem32[GPIO_OUT_REG] & self.andmask)
        enable_irq(isr)
