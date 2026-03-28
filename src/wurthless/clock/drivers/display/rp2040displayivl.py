'''
For IVL2-7/5 project - kept separate from rp2040display.py due to 5 sideset lines
'''

from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay
from wurthless.clock.common.pwmu16brightnessctrl import PwmU16BrightnessController

from machine import Pin, PWM, mem32
import rp2
from rp2 import PIO

# these match ivl clock v1 (remember to decorate with scrambledbitsdisplay!)
registerCvar("wurthless.clock.drivers.display.rp2040displayivl",
             "segment_drive_base_pin",
             "Int",
             "Segment drive base pin. Default is GPIO 5 (6,7,8,9,10,11 will also be used here)",
             5)

registerCvar("wurthless.clock.drivers.display.rp2040displayivl",
             "digit_drive_base_pin",
             "Int",
             "Digit drive base pin. Default is GPIO 12 (13,14,15 will also be used here)",
             12)

registerCvar("wurthless.clock.drivers.display.rp2040displayivl",
             "brightness_pwm_pin",
             "Int",
             "PWM pin for controlling brightness. Default is GPIO 3.",
             3)

registerCvar("wurthless.clock.drivers.display.rp2040displayivl",
             "low_power_drives",
             "Boolean",
             "If true, reduces current drive power on the segment and digit control GPIOs. Default is True.",
             True)

################################################################################################################
#
# Everything else
#
################################################################################################################

# more appropriate refresh rate is 120 Hz or so, but the PIO can't run at that low a frequency,
# so we have to use hacks to simulate that
@rp2.asm_pio(out_init=[PIO.OUT_LOW]*7, set_init=[PIO.OUT_LOW]*4)
def sevseg():
    wrap_target()
    pull(noblock)     # get whatever the CPU wants us to display
    mov(x, osr)       # push to output shift register (all values 8 bits, msb unused)
    
    # digits have to be strobed this way or else there will be ghosting
    out(pins, 8)      # clock out bits while digit disabled
    set(pins, 1)
    nop() [3]
    set(pins, 0)      # clear pins

    # inner 2 digits tend to be brighter than the outer 2
    # so they don't get strobed as fast
    out(pins, 8)      # clock out bits while digit disabled
    set(pins, 2)
    nop() [1]
    set(pins, 0)      # clear pins

    out(pins, 8)      # clock out bits while digit disabled
    set(pins, 4)
    nop() [1]
    set(pins, 0)      # clear pins.

    out(pins, 8)      # clock out bits while digit disabled
    set(pins, 8)
    nop() [3]
    set(pins, 0)      # clear pins
    
    wrap()

class Rp2040IvlDisplay(SevenSegmentDisplay):
    def __init__(self, tot):
        segment_drive_base_pin = tot.cvars().get("wurthless.clock.drivers.display.rp2040displayivl", "segment_drive_base_pin")
        digit_drive_base_pin   = tot.cvars().get("wurthless.clock.drivers.display.rp2040displayivl", "digit_drive_base_pin")
        brightness_pwm_pin     = tot.cvars().get("wurthless.clock.drivers.display.rp2040displayivl", "brightness_pwm_pin")

        # attempt to grab I/Os here by setting them all as outputs
        # it is better to have them setup in a known state than to assume the statemachine will do everything for us
        low_power_drives     = tot.cvars().get(u"wurthless.clock.drivers.display.rp2040displayivl", u"low_power_drives")   
        for i in range(segment_drive_base_pin, segment_drive_base_pin+7):
            Pin(i, Pin.OUT)
            if low_power_drives is True:
                mem32[0x4001c004 + (i*4)] = (mem32[0x4001c004 + (i*4)] & 0b11001111)
        for i in range(digit_drive_base_pin,   digit_drive_base_pin+4):
            Pin(i, Pin.OUT)
            if low_power_drives is True:
                mem32[0x4001c004 + (i*4)] = (mem32[0x4001c004 + (i*4)] & 0b11001111)
                
        self.sm = rp2.StateMachine(0,
                                   sevseg,
                                   freq=2000,
                                   out_base=Pin(segment_drive_base_pin),
                                   set_base=Pin(digit_drive_base_pin))
        
        self._brightness_ctrl = PwmU16BrightnessController(brightness_pwm_pin, 2000)

        # bring up display but in blank state.
        self.blank()
        self.sm.active(1)

    def setBrightness(self, brightness):
        self._brightness_ctrl.setBrightness(brightness)

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        self.sm.put( d | c << 8 | b << 16 | a << 24 )
