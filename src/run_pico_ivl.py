'''
IVL2-7/5 Pico driver, kept separate from run_pico.py due to massively different I/O mappings
'''

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain
from wurthless.clock.burnin import burnin

# from wurthless.clock.common.ntp4timesource import Ntp4TimeSource
from wurthless.clock.common.messages import messagesDisplayInit

from wurthless.clock.drivers.display.rp2040displayivl import Rp2040IvlDisplay
from wurthless.clock.drivers.display.colonpwmdisplay import ColonGpioDisplay
from wurthless.clock.drivers.input.gpioinputs import GpioInputs
# from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

# must-init cvars must be defined, so don't remove this
import config
from machine import Pin,UART,Timer
from wurthless.clock.drivers.nmea.nmeadevice import NmeaDevice
from wurthless.clock.drivers.nmea.nmeatimesource import NmeaTimeSource

from wurthless.clock.common.rp2040hbridgedriver import hbridge_init
from wurthless.clock.drivers.input.dstdipswitchinputs import DstDipswitchInputs

def picoIvlCommonInit(tot):
    cvars = Cvars()
    writer = TokenedCvarWriter()
    cvars.setWriter(TokenedCvarWriter())

    cvars.load()
    tot.setCvars( cvars )

    display = Rp2040IvlDisplay(tot)
    display = ColonGpioDisplay(display, 4)

    tot.setDisplay(display)
    
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "up_pin_id", 6)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "down_pin_id", 7)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "set_pin_id", 8)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "dst_pin_id", 9)
    
    inputs = GpioInputs(tot)
    
    inputs = DstDipswitchInputs(inputs)
    
    tot.setInputs( inputs )

    tot.setRtc( MicropythonRTC() )

    hbridge_init(2)

def runPicoW():
    tot = ToT()
    picoIvlCommonInit(tot)

    # display INIT
    messagesDisplayInit(tot.display())

    # install NIC and NTP timesource
    # tot.setNic( MicropythonWifiNic(tot) )
    # tot.setTimeSources( [ Ntp4TimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get(u"config.nic",u"wifi_ap_name") == u"":
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()
    clockMain(tot)


def burninPico():
    tot = ToT()
    picoIvlCommonInit(tot)



    burnin(tot)
