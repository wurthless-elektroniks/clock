#
# Platform init for ESP32-based hardware
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.display.bitbangdisplay import BitbangDisplay
from wurthless.clock.mock.nullinputs import NullInputs
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

import config

# ESP32-C3-WROOM-02 support is very limited.
# almost all accessible GPIOs are taken up by the LED matrix.
# it does work, but not reliable enough to be considered usable (yet).
def runEsp32C3Wroom02():
    tot = ToT()

    cvars = Cvars()
    writer = TokenedCvarWriter()

    # "factory" is the factory defaults
    writer.addPreflight(u"secrets/factory.ini")
    
    # "guid" is device-specific stuff (serial number, device name, etc.)
    writer.addPreflight(u"secrets/guid.ini")

    cvars.setWriter(writer)

    cvars.load()
    tot.setCvars( cvars )

    tot.setDisplay( BitbangDisplay(tot) )
    tot.setInputs( NullInputs() )
    tot.setRtc( MicropythonRTC() )

    # display INIT
    tot.display().setDigitsBinary(0b00000110, 0b00110111, 0b00000110, 0b01111000)

    # install NIC and NTP timesource
    tot.setNic( MicropythonWifiNic(tot) )
    tot.setTimeSources( [ NtpTimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get(u"config.nic",u"wifi_ap_name") == u"":
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()
    clockMain(tot)
