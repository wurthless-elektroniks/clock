'''
Split up from run_pico, it's for the Nixie prototype...
'''

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain
from wurthless.clock.burnin import burnin

from wurthless.clock.common.ntp4timesource import Ntp4TimeSource
from wurthless.clock.common.messages import messagesDisplayInit

from wurthless.clock.drivers.input.gpioinputs import GpioInputs
from wurthless.clock.drivers.display.bcdlatchdisplay import BcdLatchDisplay
from wurthless.clock.drivers.display.pwmbrightnessdisplay import PwmU16BrightnessDisplay
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

# must-init cvars must be defined, so don't remove this
import config


# Pico/Pico W share common hardware configuration for the LED matrix, switches, etc.
def picoCommonInit(tot):
    cvars = Cvars()
    writer = TokenedCvarWriter()
    cvars.setWriter(TokenedCvarWriter())

    cvars.load()
    tot.setCvars( cvars )

    display = BcdLatchDisplay(tot)
    display = PwmU16BrightnessDisplay(display, 10)

    tot.setDisplay(display)
    tot.setInputs( GpioInputs(tot) )
    tot.setRtc( MicropythonRTC() )

def runPicoW():
    tot = ToT()
    picoCommonInit(tot)

    # display INIT
    messagesDisplayInit(tot.display())

    # install NIC and NTP timesource
    tot.setNic( MicropythonWifiNic(tot) )
    tot.setTimeSources( [ Ntp4TimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get("config.clock","force_manual") is False and \
       tot.cvars().get("config.nic", "enable") and \
        tot.cvars().get("config.nic","wifi_ap_name") == "":
        tot.cvars().set("wurthless.clock.clockmain", "force_server", True)

    tot.finalize()
    clockMain(tot)
