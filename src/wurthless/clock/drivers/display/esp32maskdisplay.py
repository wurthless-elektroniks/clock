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

if sys.implementation._machine.find("ESP32C3") >= 0:
    # for esp32c3, have to check implementation, platform will be esp32 and that's too ambiguous
    import wurthless.clock.drivers.machine.esp32c3 as esp32c3
    esp32c3.configureEsp32C3IoPins()
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
             u"brightness_pwm_pin",
             u"Int",
             u"LED brightness PWM pin",
             25)

registerCvar(u"wurthless.clock.drivers.display.esp32maskdisplay",
             u"strobe_frequency",
             u"Int",
             u"Frequency at which we update the display",
             int(4*60*4))

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

        frequency = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_frequency")
        self.sm_state = 0
        self.sm_ptr = 0
        
        self.timer = Timer(0, mode=Timer.PERIODIC, freq = frequency, callback=self._strobe)

        pwm_pin = cvars.get(u"wurthless.clock.drivers.display.esp32maskdisplay", u"brightness_pwm_pin")
        
        #self.brightness_pwm = PWM(Pin(pwm_pin))
        #self.setBrightness(8)
#        Pin(pwm_pin,Pin.OUT).value(1)

    def _strobe(self,t):
        isr = disable_irq()
        mem32[GPIO_OUT_REG] = (mem32[GPIO_OUT_REG] & self.andmask) | self.digs[self.sm_ptr & 3]
        self.sm_ptr += 1
        enable_irq(isr)

    def setBrightness(self, brightness):
        pass
        #self.brightness_pwm.init(freq = 2000, duty = int(1000*((brightness / 8))+23))

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
            isr = disable_irq()
            self.digs = munged
            enable_irq(isr)
            
            self.last_digs = self.digs

    def shutdown(self):
        self.timer.deinit()
        
        # disable all digit drives so the display goes blank
        mem32[GPIO_OUT_REG] = (mem32[GPIO_OUT_REG] & self.andmask)
