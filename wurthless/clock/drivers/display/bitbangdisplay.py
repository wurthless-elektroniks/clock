#
# Generic bitbanged display for Micropython devices.
# This will typically be seen in ESP32 scenarios.
#

from machine import Pin,Timer
import time

from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.common.ioseq import IoSequencer

################################################################################################################
#
# Cvars
# Defaults assume an ESP32-C3-WROOM-02 development board
#
################################################################################################################

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_a_pin",
             u"Int",
             u"LED segment A drive pin",
             9)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_b_pin",
             u"Int",
             u"LED segment B drive pin",
             8)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_c_pin",
             u"Int",
             u"LED segment C drive pin",
             10)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_d_pin",
             u"Int",
             u"LED segment D drive pin",
             3)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_e_pin",
             u"Int",
             u"LED segment E drive pin",
             2)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_f_pin",
             u"Int",
             u"LED segment F drive pin",
             1)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"seg_g_pin",
             u"Int",
             u"LED segment G drive pin",
             0)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"digit_0_pin",
             u"Int",
             u"LED digit 0 drive pin",
             4)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"digit_1_pin",
             u"Int",
             u"LED digit 1 drive pin",
             5)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"digit_2_pin",
             u"Int",
             u"LED digit 2 drive pin",
             6)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"digit_3_pin",
             u"Int",
             u"LED digit 3 drive pin",
             7)

# no brightness control yet

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"strobe_frequency",
             u"Int",
             u"Frequency at which we update the display",
             1000)

registerCvar(u"wurthless.clock.drivers.display.bitbangdisplay",
             u"strobe_delay",
             u"Int",
             u"Delay between digit strobes in microseconds",
             1000)

# Brightness table the same as in rp2040display.py
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

class BitbangDisplayIoseq(Display):
    def __init__(self, tot):
        self.digs = 0
        
        self._buildIoSeq(tot)

        self.ioseq.exec()

    def _buildIoSeq(self, tot):
        cvars = tot.cvars()

        seg_a_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_a_pin" )
        seg_b_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_b_pin" )
        seg_c_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_c_pin" )
        seg_d_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_d_pin" )
        seg_e_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_e_pin" )
        seg_f_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_f_pin" )
        seg_g_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_g_pin" )

        dig_0_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_0_pin" )
        dig_1_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_1_pin" )
        dig_2_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_2_pin" )
        dig_3_pin = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_3_pin" )
       
        seg_pins = [ seg_a_pin, seg_b_pin, seg_c_pin, seg_d_pin, seg_e_pin, seg_f_pin, seg_g_pin ]
        dig_pins = [ dig_0_pin, dig_1_pin, dig_2_pin, dig_3_pin ]

        self.ioseq = IoSequencer()

        # this display driver assumes the direction of these pins will never change.
        # if you need to mux inputs, look elsewhere!
        for i in seg_pins + dig_pins:
            self.ioseq.assignPin(i)
            self.ioseq.setPinMode(i, Pin.OUT)

        for digit in range(0,4):
            for segment in range(0,7):
                self.ioseq.assembleOutShiftRegister(seg_pins[segment])
                self.ioseq.assemblePinValue(dig_pins[digit], 1)
                self.ioseq.assembleWAA()
                self.ioseq.assemblePinValue(dig_pins[digit], 0)
                self.ioseq.assemblePinValue(seg_pins[segment], 0)
                self.ioseq.assembleWAB()
            self.ioseq.assembleBurnShiftRegister()


    def setBrightness(self, brightness):
        brightness_period = (brightness / 8)
        self.ioseq.setA(int( 10 * brightness_period))
        self.ioseq.setB(int( 10 * (1-brightness_period)))

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        self.ioseq.setShiftRegisterValue( ( d << 24 | c << 16 | b << 8 | a ) )

class BitbangDisplay(Display):
    def __init__(self, tot):
        cvars = tot.cvars()

        # init seg drives
        self.seg_drives = [
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_a_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_b_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_c_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_d_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_e_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_f_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"seg_g_pin" ), Pin.OUT )
        ]

        self.dig_drives = [
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_0_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_1_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_2_pin" ), Pin.OUT ),
            Pin( cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"digit_3_pin" ), Pin.OUT )
        ]

        # this obeys our standard of segment A = LSB
        self.digs = [ 0b00000000, 0b00000000, 0b00000000, 0b00000000 ]
        self.setBrightness(8)

        frequency = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"strobe_frequency" )
        self.strobe_delay = cvars.get(u"wurthless.clock.drivers.display.bitbangdisplay", u"strobe_delay" ) / 1000000.0

        self.timer = Timer(0, mode=Timer.PERIODIC, freq=frequency, callback=self._strobe)

    def _strobe(self,t):
        for digit in range(0,4):
            data = self.digs[digit]
            for segment in range(0,7):
                bit = (data & 1) 
                self.seg_drives[segment].value(bit)
                data >>= 1
            self.dig_drives[digit].value(1)
            time.sleep(self.strobe_delay)
            self.dig_drives[digit].value(0)

    def setBrightness(self, brightness):
        pass

    def setDigitsBinary(self, a, b, c, d):
        a = int(a & 255)
        b = int(b & 255)
        c = int(c & 255)
        d = int(d & 255)
        
        self.digs[0] = a
        self.digs[1] = b
        self.digs[2] = c
        self.digs[3] = d
        