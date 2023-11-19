#
# Platform init for Raspberry Pi Pico W-based hardware. Import runPicoW() from your main.py file and jump to it.
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.input.gpioinputs import GpioInputs
from wurthless.clock.drivers.display.rp2040display import Rp2040Display
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

    # "factory" is the factory defaults
    writer.addPreflight(u"secrets/factory.ini")
    
    # "guid" is device-specific stuff (serial number, device name, etc.)
    writer.addPreflight(u"secrets/guid.ini")

    cvars.setWriter(writer)

    cvars.load()
    tot.setCvars( cvars )

    tot.setDisplay( Rp2040Display(tot) )
    tot.setInputs( GpioInputs(tot) )
    tot.setRtc( MicropythonRTC() )

#############################################################################
#
# runPicoW(): init base RPi Pico W hardware; Wifi enabled, NTP timesource
#
#############################################################################
def runPicoW():
    tot = ToT()
    picoCommonInit(tot)

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

#############################################################################
#
# runPicoW(): init base RPi Pico hardware; no timesources, internal RTC only
#
############################################################################
# #
def runPico():
    tot = ToT()
    picoCommonInit(tot)

    tot.finalize()
    clockMain(tot)

