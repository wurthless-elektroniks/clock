#
# Display driver that accesses the ESP32 GPIOs directly.
#

import sys
import time
from micropython import const
from machine import Pin,Timer,mem32,disable_irq,enable_irq,PWM
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.api.display import Display

# i'm serious. we are accessing the hardware directly. it's too slow otherwise.
# DANGER! this I/O register changes depending on what ESP32 we are using.

# for esp32c3, have to check implementation, platform will be esp32 and that's too ambiguous
if sys.implementation._machine.find("ESP32C3") >= 0:
    GPIO_OUT_REG = 0x60004004

    # micropython sucks and will not let us grab pins 18 or 19 as I/Os
    # although, hilariously, it allows us to try grabbing pins 11-17.
    print(u"******* ESP32-C3 detected. hacking around micropython limitations *******")
    print(u"killing USB-JTAG. if i don't see you on the other side, adios!")

    # disable USB PHY
    mem32[0x60043018] = 0x00000000

    print(u"grabbing pins 18/19 and setting them up as outputs")

    # set pins 18/19 as outputs
    mem32[0x60004024] |= (1 << 18) | (1 << 19)

    # configure pins 18/19 on I/O mux to match how the others are configured.
    # unfortunately, it seems pins 18/19 are limited in how much current they
    # can deliver so those segments might be dimmer than the others.
    # more testing to be done later.
    #
    #                     fedcba9876543210
    mem32[0x6000904C] = 0b0000111101101011
    mem32[0x60009050] = 0b0000111101101011

    print(u"esp32c3 platform configured. have a nice day!")
elif sys.platform == u'esp32':
    GPIO_OUT_REG = 0x3FF44004
else:
    print(u"DANGER: platform not recognized (%s). defaulting to default esp32 gpio register. you're entering very dangerous territory if you start execution."%(sys.platform))
    GPIO_OUT_REG = 0x3FF44004

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_a_pin",
             u"Int",
             u"LED segment A drive pin",
             19)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_b_pin",
             u"Int",
             u"LED segment B drive pin",
             18)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_c_pin",
             u"Int",
             u"LED segment C drive pin",
             10)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_d_pin",
             u"Int",
             u"LED segment D drive pin",
             3)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_e_pin",
             u"Int",
             u"LED segment E drive pin",
             2)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_f_pin",
             u"Int",
             u"LED segment F drive pin",
             1)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_g_pin",
             u"Int",
             u"LED segment G drive pin",
             0)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_0_pin",
             u"Int",
             u"LED digit 0 drive pin",
             5)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_1_pin",
             u"Int",
             u"LED digit 1 drive pin",
             6)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_2_pin",
             u"Int",
             u"LED digit 2 drive pin",
             7)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_3_pin",
             u"Int",
             u"LED digit 3 drive pin",
             8)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_frequency",
             u"Int",
             u"Frequency at which we update the display",
             int(4*60*4))

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_wait_ticks",
             u"Int",
             u"Number of ticks to wait before advancing to next display digit",
             int(8))


SM_CLOCK_NEXT_DIGIT  = 0
SM_WAIT_IN_ON_STATE  = 1
SM_CLEAR_DISPLAY     = 2
SM_WAIT_IN_OFF_STATE = 3

class Esp32MaskDisplay(Display):
    def __init__(self, tot):
        cvars = tot.cvars()

        seg_a_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_a_pin" )
        seg_b_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_b_pin" )
        seg_c_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_c_pin" )
        seg_d_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_d_pin" )
        seg_e_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_e_pin" )
        seg_f_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_f_pin" )
        seg_g_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_g_pin" )

        dig_0_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_0_pin" )
        dig_1_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_1_pin" )
        dig_2_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_2_pin" )
        dig_3_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_3_pin" )
       
        self.seg_pins = [ seg_a_pin, seg_b_pin, seg_c_pin, seg_d_pin, seg_e_pin, seg_f_pin, seg_g_pin ]
        self.dig_pins = [ dig_0_pin, dig_1_pin, dig_2_pin, dig_3_pin ]

        # force system to mark all pins as outputs
        for p in self.seg_pins+self.dig_pins:
            if sys.implementation._machine.find("ESP32C3") >= 0 and p in [18,19]:
                # we've already tried grabbing those, don't do it again or we'll get exceptions
                pass
            else:
                Pin(p,Pin.OUT).value(0)

        self.digs = [ 0b00000000, 0b00000000, 0b00000000, 0b00000000 ]
        self.last_digs = self.digs

        # compute andmask
        andmask = 0
        for digit in range(0,4):
            andmask |= (1 << self.dig_pins[digit])
            for segment in range(0,7):
                andmask |= (1 << self.seg_pins[segment])
        self.andmask = ~andmask

        frequency = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_frequency" )
        self.strobe_wait_ticks = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_wait_ticks" )

        self.sm_state = 0
        self.sm_ptr = 0
        self.sm_waits = 0

        self.timer = Timer(0, mode=Timer.PERIODIC, freq = frequency, callback=self._strobe)

        self.brightness_pwm = PWM(Pin(25))
        self.setBrightness(8)

    def _strobe(self,t):
        isr = disable_irq()
        mem32[GPIO_OUT_REG] = (mem32[GPIO_OUT_REG] & self.andmask) | self.digs[self.sm_ptr]
        self.sm_ptr += 1
        self.sm_ptr &= 3
        enable_irq(isr)

    def setBrightness(self, brightness):
        self.brightness_pwm.init(freq = 2000, duty = int(1000*((brightness / 8))+23))

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

        if self.last_digs != munged:
            self.digs = munged
            self.last_digs = self.digs
