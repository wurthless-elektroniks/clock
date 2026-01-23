
from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain
from wurthless.clock.burnin import burnin

from wurthless.clock.common.ntp4timesource import Ntp4TimeSource
from wurthless.clock.common.messages import messagesDisplayInit

from wurthless.clock.drivers.display.shiftydisplay import ShiftyDisplay
from wurthless.clock.drivers.display.scrambledbitsdisplay import ScrambledBitsDisplay


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

def picoVfdCommonInit(tot):
    cvars = Cvars()
    writer = TokenedCvarWriter()
    cvars.setWriter(TokenedCvarWriter())

    cvars.load()
    tot.setCvars( cvars )
    
    display = ShiftyDisplay(tot)

    # the iv22 display board segments are wired according to how they are
    # in a datasheet. this is a mistake on my end but it turns out it's easier
    # to route the PCB this way. might end up changing this for v2...
    display = ScrambledBitsDisplay(display, {
        0: 0,
        1: 5,
        2: 2,
        3: 1,
        4: 3,
        5: 6,
        6: 4
    })
    
    tot.setDisplay(display)
    
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "up_pin_id",  7)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "down_pin_id", 8)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "set_pin_id",  9)
    tot.cvars().set("wurthless.clock.drivers.input.gpioinputs", "dst_pin_id",  11)
    
    inputs = GpioInputs(tot)
    inputs = DstDipswitchInputs(inputs)
    tot.setInputs( inputs )
    tot.setRtc( MicropythonRTC() )

    # TODO: resolve the hardware bug with the hbridge driver, it's not outputting
    # enough voltage to drive the heaters... good thing the tubes work without
    # the hbridge driver in place.

    # hbridge_init(16)

def runPicoW():
    tot = ToT()
    picoVfdCommonInit(tot)

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
