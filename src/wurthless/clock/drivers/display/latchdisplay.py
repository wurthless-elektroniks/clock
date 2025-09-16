'''
Display with four SN74HC373s.
Used for first version of IV-11 driver.
'''


import time
from machine import Pin, PWM
from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_a_pin",
             "Int",
             "LED segment A drive pin",
             16)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_b_pin",
             "Int",
             "LED segment B drive pin",
             17)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_c_pin",
             "Int",
             "LED segment C drive pin",
             18)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_d_pin",
             "Int",
             "LED segment D drive pin",
             19)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_e_pin",
             "Int",
             "LED segment E drive pin",
             20)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_f_pin",
             "Int",
             "LED segment F drive pin",
             21)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "seg_g_pin",
             "Int",
             "LED segment G drive pin",
             22)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "digit_0_pin",
             "Int",
             "LED digit 0 drive pin",
             12)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "digit_1_pin",
             "Int",
             "LED digit 1 drive pin",
             13)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "digit_2_pin",
             "Int",
             "LED digit 2 drive pin",
             14)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "digit_3_pin",
             "Int",
             "LED digit 3 drive pin",
             15)

registerCvar("wurthless.clock.drivers.display.latchdisplay",
             "brightness_pwm_pin",
             "Int",
             "LED brightness PWM pin",
             10)


class LatchDisplay(SevenSegmentDisplay):
    def __init__(self, tot):
        cvars = tot.cvars()

        seg_a_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_a_pin" )
        seg_b_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_b_pin" )
        seg_c_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_c_pin" )
        seg_d_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_d_pin" )
        seg_e_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_e_pin" )
        seg_f_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_f_pin" )
        seg_g_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "seg_g_pin" )

        dig_0_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "digit_0_pin" )
        dig_1_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "digit_1_pin" )
        dig_2_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "digit_2_pin" )
        dig_3_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "digit_3_pin" )
        
        self.seg_pins = [ seg_a_pin, seg_b_pin, seg_c_pin, seg_d_pin, seg_e_pin, seg_f_pin, seg_g_pin ]
        self.dig_pins = [ dig_0_pin, dig_1_pin, dig_2_pin, dig_3_pin ]

        pwm_pin = cvars.get("wurthless.clock.drivers.display.latchdisplay", "brightness_pwm_pin")
        self.brightness_pwm = PWM(Pin(pwm_pin))
        self.setBrightness(8)

    def setBrightness(self, brightness):
        duty = int(1000*((brightness / 8))+23)
        if self._halfbright:
            duty >>= 1
        self.brightness_pwm.init(freq = self.strobe_frequency * 2, duty=duty)

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 0x7F)
        b = int(b & 0x7F)
        c = int(c & 0x7F)
        d = int(d & 0x7F)
        
        vals = [a,b,c,d]
        masks = [ 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80 ]
        
        for i,dig_pin in enumerate(self.dig_pins):
            for j,seg_pin in enumerate(self.seg_pins):
                seg_pin.value( (vals[i] & masks[j]) != 0 )
            dig_pin.value(1)
            time.sleep(0.001)
            dig_pin.value(0)

    def shutdown(self):
        pass
