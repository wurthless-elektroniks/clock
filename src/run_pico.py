#
# Platform init for Raspberry Pi Pico W-based hardware. Import runPicoW() from your main.py file and jump to it.
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain
from wurthless.clock.burnin import burnin

from wurthless.clock.common.ntp4timesource import Ntp4TimeSource

from wurthless.clock.drivers.input.gpioinputs import GpioInputs
from wurthless.clock.drivers.display.rp2040display import Rp2040Display
from wurthless.clock.drivers.display.invertedbitdisplay import InvertedBitDisplay 
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

# must-init cvars must be defined, so don't remove this
import config

from machine import Pin,UART
from wurthless.clock.drivers.nmea.nmeadevice import NmeaDevice
from wurthless.clock.drivers.nmea.nmeatimesource import NmeaTimeSource
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits

# Pico/Pico W share common hardware configuration for the LED matrix, switches, etc.
def picoCommonInit(tot,invert_bits):
    cvars = Cvars()
    writer = TokenedCvarWriter()

    # "factory" is the factory defaults
    writer.addPreflight(u"secrets/factory.ini")
    
    # "guid" is device-specific stuff (serial number, device name, etc.)
    writer.addPreflight(u"secrets/guid.ini")

    cvars.setWriter(writer)

    cvars.load()
    tot.setCvars( cvars )

    display = Rp2040Display(tot)
    if invert_bits is True:
        display = InvertedBitDisplay(display)
    tot.setDisplay(display)
    tot.setInputs( GpioInputs(tot) )
    tot.setRtc( MicropythonRTC() )


#############################################################################
#
# runPicoW(): init base RPi Pico W hardware; Wifi enabled, NTP timesource
#
#############################################################################
def runPicoW(invert_bits=False):
    tot = ToT()
    picoCommonInit(tot,invert_bits)

    # display INIT
    tot.display().setDigitsBinary(0b00000110, 0b00110111, 0b00000110, 0b01111000)

    # install NIC and NTP timesource
    tot.setNic( MicropythonWifiNic(tot) )
    tot.setTimeSources( [ Ntp4TimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get(u"config.nic",u"wifi_ap_name") == u"":
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()
    clockMain(tot)


def runPicoGnss(invert_bits=False):
    tot = ToT()
    picoCommonInit(tot,invert_bits)

    # display INIT
    tot.display().setDigitsBinary(0b00000110, 0b00110111, 0b00000110, 0b01111000)

    nmea = NmeaDevice(UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1), timeout=300))

    # display number of GNSS satellites in view until the NMEA device signals it's ready
    while nmea.isUp() is False:
        digs = sevensegNumbersToDigits(None, 5, nmea.getSatellitesVisible() / 10, nmea.getSatellitesVisible() % 10)
        tot.display().setDigitsBinary(digs[0],digs[1],digs[2],digs[3])
    
    tot.setTimeSources( [ NmeaTimeSource(nmea) ] )
    
    tot.finalize()
    clockMain(tot)

#############################################################################
#
# runPicoW(): init base RPi Pico hardware; no timesources, internal RTC only
#
############################################################################
# #
def runPico(invert_bits=False):
    tot = ToT()
    picoCommonInit(tot,invert_bits)

    tot.finalize()
    clockMain(tot)

def burninPico(invert_bits=False):
    tot = ToT()
    picoCommonInit(tot,invert_bits)

    burnin(tot)