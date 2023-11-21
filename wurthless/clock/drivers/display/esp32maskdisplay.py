#
# Display driver that accesses the ESP32 GPIOs directly.
#

import sys
import time
from micropython import const
from machine import Pin,Timer,mem32,disable_irq,enable_irq
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.api.display import Display

# i'm serious. we are accessing the hardware directly. it's too slow otherwise.
# DANGER! this I/O register changes depending on what ESP32 we are using.
if sys.platform == u'esp32':
    GPIO_OUT_REG = 0x3FF44004
elif sys.platform == u'esp32c3':
    GPIO_OUT_REG = 0x60004004
else:
    print(u"DANGER: platform not recognized (%s). defaulting to default esp32 gpio register. you're entering very dangerous territory if you start execution."%(sys.platform))
    GPIO_OUT_REG = 0x3FF44004

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_a_pin",
             u"Int",
             u"LED segment A drive pin",
             9)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"seg_b_pin",
             u"Int",
             u"LED segment B drive pin",
             8)

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
             4)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_1_pin",
             u"Int",
             u"LED digit 1 drive pin",
             5)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_2_pin",
             u"Int",
             u"LED digit 2 drive pin",
             6)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"digit_3_pin",
             u"Int",
             u"LED digit 3 drive pin",
             7)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_frequency",
             u"Int",
             u"Frequency at which we update the display",
             int(11100))

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_wait_ticks",
             u"Int",
             u"Number of ticks to wait before advancing to next display digit",
             int(11))


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
            Pin(p,Pin.OUT).value(0)

        self.digs = [ 0b00000000, 0b00000000, 0b00000000, 0b00000000 ]

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
        self.setBrightness(8)

        self.timer = Timer(0, mode=Timer.PERIODIC, freq=frequency, callback=self._strobe)

    def _strobe(self,t):
        isr = disable_irq()
        if self.sm_state == SM_WAIT_IN_ON_STATE or self.sm_state == SM_WAIT_IN_OFF_STATE:    
            if self.sm_waits > 0:
                self.sm_waits -= 1
            else:
               self.sm_state += 1
               self.sm_state &= 3
        elif self.sm_state == SM_CLEAR_DISPLAY:
            if self.sm_off_ticks == 0:
                self.sm_state = 0
            else:
                mem32[GPIO_OUT_REG] = 0
                self.sm_waits = self.sm_off_ticks
                self.sm_state += 1
        else:
            mem32[GPIO_OUT_REG] = self.digs[self.sm_ptr]
            self.sm_ptr += 1
            self.sm_ptr &= 3
            self.sm_waits = self.sm_on_ticks
            self.sm_state += 1
        enable_irq(isr)

    def setBrightness(self, brightness):
        period = (brightness / 8)
        self.sm_on_ticks  = int(self.strobe_wait_ticks * period)
        self.sm_off_ticks = int(self.strobe_wait_ticks * (1-period))

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
        self.digs = munged
