#
# Seven-segment display driver for Raspberry Pi Pico PIO subsystem.
#
# The PIO driver code is a lame copypaste from https://wokwi.com/projects/300936948537623048
# Code assumes the following:
# - Segment drives on GPIOs 16~22 
# - Column drives on GPIOs 12~15
# - PWM master output control (for brightness/current flow restriction) on GPIO 10
#

from wurthless.clock.api.display import Display
from wurthless.clock.cvars import registerCvar

from machine import Pin, PWM
import rp2
from rp2 import PIO

################################################################################################################
#
# Cvars
#
################################################################################################################

# pins are reconfigurable in case of PCB layout changess
registerCvar(u"wurthless.clock.pico.picodisplay",
             u"segment_drive_base_pin",
             u"Int",
             u"LED matrix segment drive base pin. Default is GPIO 16 (17,18,19,20,21,22 will also be used here)",
             16)

registerCvar(u"wurthless.clock.pico.picodisplay",
             u"digit_drive_base_pin",
             u"Int",
             u"LED matrix digit drive base pin. Default is GPIO 12 (13,14,15 will also be used here)",
             12)

registerCvar(u"wurthless.clock.pico.picodisplay",
             u"brightness_pwm_pin",
             u"Int",
             u"PWM pin for controlling brightness. Default is GPIO 10.",
             10)

# brightness table as frequency/duty cycle.
# you might need to change these if there is no resistor in-line with the master output transistor's base,
# or else you run the risk of frying the LEDs.
# these assume that there's a resistor in-line or that the LEDs can tolerate 3v3 directly.
# in my own experience it's fine to use a 2k resistor on the base of the master (brightness) transistor
# and not do a whole lot else.
DEFAULT_BRIGHTNESS_TABLE = [
    [    0,     0 ],
    [    0,     0 ],
    [    0,     0 ],
    [    0,     0 ],
    [    0,     0 ],
    [    0,     0 ],
    [    0,     0 ],
    [ 2000, 65535 ]
]

################################################################################################################
#
# Everything else
#
################################################################################################################

@rp2.asm_pio(out_init=[PIO.OUT_LOW]*7, sideset_init=[PIO.OUT_LOW]*4)
def sevseg():
    wrap_target()
    label("0")
    pull(noblock)           .side(0)      # 0
    mov(x, osr)             .side(0)      # 1
    out(pins, 8)            .side(1)      # 2
    out(pins, 8)            .side(2)      # 3
    out(pins, 8)            .side(4)      # 4
    out(pins, 8)            .side(8)      # 5
    jmp("0")                .side(0)      # 6
    wrap()

class PicoDisplay(Display):
    def __init__(self, tot):
        segment_drive_base_pin = tot.cvars().get(u"wurthless.clock.pico.picodisplay", u"segment_drive_base_pin")
        digit_drive_base_pin   = tot.cvars().get(u"wurthless.clock.pico.picodisplay", u"digit_drive_base_pin")
        brightness_pwm_pin     = tot.cvars().get(u"wurthless.clock.pico.picodisplay", u"brightness_pwm_pin")

        # init brightness table here...

        self.sm = rp2.StateMachine(0, sevseg, freq=2000, out_base=Pin(segment_drive_base_pin), sideset_base=Pin(digit_drive_base_pin))
        self.brightness_pwm = PWM(Pin(brightness_pwm_pin))
        
        # bring up display but in blank state.
        self.setBrightness(8)
        self.setDigitsBinary(0,0,0,0)
        self.sm.active(1)

    def setBrightnessPwmRaw(self, freq, duty):
        self.brightness_pwm.freq(freq)
        self.brightness_pwm.duty_u16(duty)

    def setBrightness(self, brightness):
        if brightness < 1:
            brightness = 1
        if brightness > 8:
            brightness = 8

        brightness -= 1
        self.setBrightnessPwmRaw( BRIGHTNESS_TABLE[brightness][0], BRIGHTNESS_TABLE[brightness][1] )

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        self.sm.put( d | c << 8 | b << 16 | a << 24 )

