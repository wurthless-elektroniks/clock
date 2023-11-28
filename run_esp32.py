#
# Platform init for ESP32-based hardware
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.display.esp32maskdisplay import Esp32MaskDisplay
from wurthless.clock.mock.nullinputs import NullInputs
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

import config

from machine import Pin

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

    # BEFORE the LED matrix starts up, check pin 0 status.
    # we don't have enough I/Os to allow the user to re-enter config mode!
    bootpin = Pin(0, Pin.IN, Pin.PULL_UP)
    if bootpin.value() == 0:
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.setDisplay( Esp32MaskDisplay(tot) )
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

def runEsp32Wroom32E():
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

    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_a_pin", 15 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_b_pin", 2)
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_c_pin", 0 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_d_pin", 4 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_e_pin", 16 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_f_pin", 17 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"seg_g_pin", 5 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_0_pin", 18 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_1_pin", 19 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_2_pin", 21 )
    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"digit_3_pin", 22 )

    cvars.set(u"wurthless.clock.drivers.display.esp32maskdisplay", u"strobe_frequency", 4*60 )

    tot.setDisplay( Esp32MaskDisplay(tot) )
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