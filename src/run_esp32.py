#
# Platform init for ESP32-based hardware
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.messages import messagesDisplayInit
from wurthless.clock.common.ntp4timesource import Ntp4TimeSource

from wurthless.clock.drivers.display.esp32maskdisplay import Esp32MaskDisplay

from wurthless.clock.drivers.input.esp32gpioinputs import Esp32GpioInputs
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.display.invertedbitdisplay import InvertedBitDisplay

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

import config

def runEsp32Wroom32E(invert_bits=False):
    tot = ToT()

    cvars = Cvars()
    cvars.setWriter(TokenedCvarWriter())

    cvars.load()
    tot.setCvars( cvars )

    cvars.configure(u"wurthless.clock.drivers.display.esp32maskdisplay",
                    { 
                       u"strobe_fast": True
                    })

    # not enough CPU time in config mode to run the display
    cvars.set("wurthless.clock.webserver", "disable_display_when_serving", True)
    cvars.set("wurthless.clock.webserver", "server_active_pin", 26)

    display = Esp32MaskDisplay(tot)
    if invert_bits is True:
        display = InvertedBitDisplay(display)

    tot.setDisplay( display )
    tot.setInputs( Esp32GpioInputs(tot) )
    tot.setRtc( MicropythonRTC() )

    # display INIT
    messagesDisplayInit(tot.display())

    # install NIC and NTP timesource
    tot.setNic( MicropythonWifiNic(tot) )
    tot.setTimeSources( [ Ntp4TimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get(u"config.nic",u"wifi_ap_name") == u"":
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()
    clockMain(tot)
