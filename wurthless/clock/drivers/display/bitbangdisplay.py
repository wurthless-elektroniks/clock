#
# Generic bitbanged display for Micropython devices.
# This will typically be seen in ESP32 scenarios.
#

from machine import Pin,PWM,Timer
from uasyncio import Lock
import time

from wurthless.clock.api.display import Display
from wurthless.clock.cvars.cvars import registerCvar

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

class BitbangDisplay(Display):
    def __init__(self, tot):
        self.lock = Lock()

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
        