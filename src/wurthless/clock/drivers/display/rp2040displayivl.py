'''
For IVL2-7/5 project - kept separate from rp2040display.py due to 5 sideset lines
'''

from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay

from machine import Pin, PWM, mem32
import rp2
from rp2 import PIO


DIGIT_DRIVE_BASE_PIN = 11 # + 12, 13, 14
SEGMENT_DRIVE_BASE_PIN = 16 # + 17, 18, 19, 20, 21, 22
PWM_PIN = 10

registerCvar(u"wurthless.clock.drivers.display.rp2040displayivl",
             u"low_power_drives",
             u"Boolean",
             u"If true, reduces current drive power on the segment and digit control GPIOs. Default is True.",
             True)

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
    
    # digits have to be strobed this way or else there will be ghosting
    out(pins, 8)            .side(0)      # clock out bits while digit disabled
    nop()                   .side(1)      # enable the digit
    nop()                   .side(1)
    nop()                   .side(1)
    nop()                   .side(1)
    set(pins, 0)            .side(0)     # clear pins

    # inner 2 digits tend to be brighter than the outer 2
    # so they don't get strobed as fast
    out(pins, 8)            .side(0)
    nop()                   .side(2)
    nop()                   .side(2)
    set(pins, 0)            .side(0)

    out(pins, 8)            .side(0)
    nop()                   .side(4)
    nop()                   .side(4)
    set(pins, 0)            .side(0)
    
    out(pins, 8)            .side(0)
    nop()                   .side(8)
    nop()                   .side(8)
    nop()                   .side(8)
    nop()                   .side(8)
    set(pins, 0)            .side(0)
    
    jmp("0")                .side(0)      # blank display and repeat
    wrap()

class Rp2040IvlDisplay(SevenSegmentDisplay):
    def __init__(self, tot):
        segment_drive_base_pin = SEGMENT_DRIVE_BASE_PIN
        digit_drive_base_pin   = DIGIT_DRIVE_BASE_PIN
        brightness_pwm_pin     = PWM_PIN

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
                
        # init brightness table here...

        self.sm = rp2.StateMachine(0, sevseg, freq=2000, out_base=Pin(segment_drive_base_pin), sideset_base=Pin(digit_drive_base_pin))
        self.brightness_pwm = PWM(Pin(brightness_pwm_pin, Pin.OUT))

        # bring up display but in blank state.
        self.setBrightness(8)
        self.blank()
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
        self.setBrightnessPwmRaw( DEFAULT_BRIGHTNESS_TABLE[brightness][0], DEFAULT_BRIGHTNESS_TABLE[brightness][1] )

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        self.sm.put( d | c << 8 | b << 16 | a << 24 )

