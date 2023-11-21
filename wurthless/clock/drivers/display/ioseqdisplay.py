#
# Generic bitbanged display driven by the I/O sequencer.
#

from machine import Pin

from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.common.ioseq import IoSequencer
from wurthless.clock.api.display import Display

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_a_pin",
             u"Int",
             u"LED segment A drive pin",
             9)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_b_pin",
             u"Int",
             u"LED segment B drive pin",
             8)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_c_pin",
             u"Int",
             u"LED segment C drive pin",
             10)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_d_pin",
             u"Int",
             u"LED segment D drive pin",
             3)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_e_pin",
             u"Int",
             u"LED segment E drive pin",
             2)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_f_pin",
             u"Int",
             u"LED segment F drive pin",
             1)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"seg_g_pin",
             u"Int",
             u"LED segment G drive pin",
             0)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"digit_0_pin",
             u"Int",
             u"LED digit 0 drive pin",
             4)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"digit_1_pin",
             u"Int",
             u"LED digit 1 drive pin",
             5)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"digit_2_pin",
             u"Int",
             u"LED digit 2 drive pin",
             6)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"digit_3_pin",
             u"Int",
             u"LED digit 3 drive pin",
             7)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"tickrate_hz",
             u"Int",
             u"Frequency at which the ioseq statemachine is advanced. Default is 100 kHz.",
             100000)

registerCvar(u"wurthless.clock.drivers.display.ioseqdisplay",
             u"strobe_delay",
             u"Int",
             u"Delay between digit strobes in ticks. Brightness is calculated using this value.",
             250)

'''
Builds a generic ioseq statemachine program that can be used elsewhere.

skip_digit_0 is an argument needed for any program that needs to multiplex I/Os.
How that is handled depends on the board.
'''
def assembleGenericIoseqProgram(ioseq, seg_pins, dig_pins, skip_digit_0 = False):
    for digit in range(0 if skip_digit_0 is False else 1,4):
        for segment in range(0,7):
            ioseq.assembleOutShiftRegister(seg_pins[segment])
        ioseq.assemblePinValue(dig_pins[digit], 1)
        ioseq.assembleWAA()
        ioseq.assemblePinValue(dig_pins[digit], 0)
        ioseq.assembleWAB()

class IoseqDisplay(Display):
    def __init__(self, tot):
        self.digs = 0
        
        self._buildIoSeq(tot)

        self.tickrate      = tot.cvars().get(u"wurthless.clock.drivers.display.ioseqdisplay", u"tickrate_hz" ) 
        self.strobe_delay  = tot.cvars().get(u"wurthless.clock.drivers.display.ioseqdisplay", u"strobe_delay" ) 

        self.ioseq.exec(self.tickrate)

    def _buildIoSeq(self, tot):
        cvars = tot.cvars()

        seg_a_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_a_pin" )
        seg_b_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_b_pin" )
        seg_c_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_c_pin" )
        seg_d_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_d_pin" )
        seg_e_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_e_pin" )
        seg_f_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_f_pin" )
        seg_g_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"seg_g_pin" )

        dig_0_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"digit_0_pin" )
        dig_1_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"digit_1_pin" )
        dig_2_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"digit_2_pin" )
        dig_3_pin = cvars.get(u"wurthless.clock.drivers.display.ioseqdisplay", u"digit_3_pin" )
       
        seg_pins = [ seg_a_pin, seg_b_pin, seg_c_pin, seg_d_pin, seg_e_pin, seg_f_pin, seg_g_pin ]
        dig_pins = [ dig_0_pin, dig_1_pin, dig_2_pin, dig_3_pin ]

        self.ioseq = IoSequencer()

        # this display driver assumes the direction of these pins will never change.
        # if you need to mux inputs, look elsewhere!
        for i in seg_pins + dig_pins:
            self.ioseq.assignPin(i)
            self.ioseq.setPinMode(i, Pin.OUT)

        assembleGenericIoseqProgram(self.ioseq,seg_pins,dig_pins)

    def setBrightness(self, brightness):
        brightness_period = (brightness / 8)
        self.ioseq.setA(int( self.strobe_delay * brightness_period))
        self.ioseq.setB(int( self.strobe_delay * (1.0-brightness_period)))

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 0x7F)
        b = int(b & 0x7F)
        c = int(c & 0x7F)
        d = int(d & 0x7F)
        v = d
        v <<= 7
        v |= c
        v <<= 7
        v |= b
        v <<= 7
        v |= a
        self.ioseq.setShiftRegisterValue( v )
