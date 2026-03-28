#
# Seven-segment display driver for Raspberry Pi Pico PIO subsystem.
#
# The PIO driver code is a lame copypaste from https://wokwi.com/projects/300936948537623048
#
# Code assumes the following:
# - Segment drives on GPIOs 16~22 
# - Column drives on GPIOs 12~15
# - PWM master output control (for brightness/current flow restriction) on GPIO 10
#

from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay
from wurthless.clock.common.pwmu16brightnessctrl import PwmU16BrightnessController

from machine import Pin, PWM, mem32
import rp2
from rp2 import PIO

################################################################################################################
#
# Cvars
#
################################################################################################################

# pins are reconfigurable in case of PCB layout changess
registerCvar(u"wurthless.clock.drivers.display.rp2040display",
             u"segment_drive_base_pin",
             u"Int",
             u"LED matrix segment drive base pin. Default is GPIO 16 (17,18,19,20,21,22 will also be used here)",
             16)

registerCvar(u"wurthless.clock.drivers.display.rp2040display",
             u"digit_drive_base_pin",
             u"Int",
             u"LED matrix digit drive base pin. Default is GPIO 12 (13,14,15 will also be used here)",
             12)

registerCvar(u"wurthless.clock.drivers.display.rp2040display",
             u"brightness_pwm_pin",
             u"Int",
             u"PWM pin for controlling brightness. Default is GPIO 10.",
             10)

registerCvar(u"wurthless.clock.drivers.display.rp2040display",
             u"low_power_drives",
             u"Boolean",
             u"If true, reduces current drive power on the segment and digit control GPIOs. Default is True.",
             True)

################################################################################################################
#
# Everything else
#
################################################################################################################

# Copypasted code, but now that I know how it works, here are comments.
# Segments are on the output pins, digit drives are on the sideset pins.
@rp2.asm_pio(out_init=[PIO.OUT_LOW]*7, sideset_init=[PIO.OUT_LOW]*4)
def sevseg():
    wrap_target()
    label("0")
    pull(noblock)           .side(0)      # get whatever the CPU wants us to display
    mov(x, osr)             .side(0)      # push to output shift register (all values 8 bits, msb unused)
    out(pins, 8)            .side(1)      # display digit 3 (display is rendered in reverse)
    out(pins, 8)            .side(2)      # display digit 2
    out(pins, 8)            .side(4)      # display digit 1
    out(pins, 8)            .side(8)      # display digit 0
    jmp("0")                .side(0)      # blank display and repeat
    wrap()

class Rp2040Display(SevenSegmentDisplay):
    def __init__(self, tot):
        segment_drive_base_pin = tot.cvars().get(u"wurthless.clock.drivers.display.rp2040display", u"segment_drive_base_pin")
        digit_drive_base_pin   = tot.cvars().get(u"wurthless.clock.drivers.display.rp2040display", u"digit_drive_base_pin")
        brightness_pwm_pin     = tot.cvars().get(u"wurthless.clock.drivers.display.rp2040display", u"brightness_pwm_pin")

        # attempt to grab I/Os here by setting them all as outputs
        # it is better to have them setup in a known state than to assume the statemachine will do everything for us
        low_power_drives     = tot.cvars().get(u"wurthless.clock.drivers.display.rp2040display", u"low_power_drives")   
        for i in range(segment_drive_base_pin, segment_drive_base_pin+7):
            Pin(i, Pin.OUT)
            if low_power_drives is True:
                mem32[0x4001c004 + (i*4)] = (mem32[0x4001c004 + (i*4)] & 0b11001111)
        for i in range(digit_drive_base_pin,   digit_drive_base_pin+4):
            Pin(i, Pin.OUT)
            if low_power_drives is True:
                mem32[0x4001c004 + (i*4)] = (mem32[0x4001c004 + (i*4)] & 0b11001111)
                
        # init brightness table here...

        self.sm = rp2.StateMachine(0, sevseg, freq=2000, out_base=Pin(segment_drive_base_pin), sideset_base=Pin(digit_drive_base_pin))

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

