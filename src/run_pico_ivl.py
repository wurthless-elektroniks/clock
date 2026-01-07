'''
IVL2-7/5 Pico driver, kept separate from run_pico.py due to massively different I/O mappings
'''

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain
from wurthless.clock.burnin import burnin

from wurthless.clock.common.ntp4timesource import Ntp4TimeSource
from wurthless.clock.common.messages import messagesDisplayInit

from wurthless.clock.drivers.display.rp2040displayivl import Rp2040IvlDisplay
from wurthless.clock.drivers.display.colonpwmdisplay import ColonGpioDisplay
from wurthless.clock.drivers.display.scrambledbitsdisplay import ScrambledBitsDisplay, REVERSED_BITS_MAPPING
from wurthless.clock.drivers.display.reverseddigitsdisplay import ReversedDigitsDisplay
from wurthless.clock.drivers.input.resetkeycomboinputs import ResetKeycomboInputs
from wurthless.clock.drivers.input.gpioinputs import GpioInputs
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

# must-init cvars must be defined, so don't remove this
import config
from machine import Pin,UART,Timer

from wurthless.clock.common.rp2040hbridgedriver import hbridge_init
from wurthless.clock.drivers.input.dstdipswitchinputs import DstDipswitchInputs

def picoIvlCommonInit(tot):
    cvars = Cvars()
    writer = TokenedCvarWriter()
    cvars.setWriter(TokenedCvarWriter())

    cvars.load()
    tot.setCvars( cvars )
    
    display = Rp2040IvlDisplay(tot)

    # needed for hw bug on v1 where the digits are wired in reverse order
    display = ReversedDigitsDisplay(display)

    display = ScrambledBitsDisplay(display, REVERSED_BITS_MAPPING)
    
    display = ColonGpioDisplay(display, 4)
    tot.setDisplay(display)
    
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "up_pin_id",  19)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "down_pin_id", 18)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "set_pin_id",  17)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "dst_pin_id",  16)
    
    inputs = GpioInputs(tot)
    inputs = ResetKeycomboInputs(inputs)
    inputs = DstDipswitchInputs(inputs)
    tot.setInputs( inputs )
    tot.setRtc( MicropythonRTC() )

    hbridge_init(20)

def runPicoW():
    tot = ToT()
    picoIvlCommonInit(tot)

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

