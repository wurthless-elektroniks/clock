#
# Platform init for ESP32-based hardware
#

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.display.esp32maskdisplay import Esp32MaskDisplay

from wurthless.clock.drivers.input.gpioinputs import GpioInputs
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.drivers.display.invertedbitdisplay import InvertedBitDisplay 
from wurthless.clock.drivers.display.cacheddisplay import CachedDisplay 

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

import config


def runEsp32Wroom32E(invert_bits=False):
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

    # pin assignments on v7
    cvars.configure(u"wurthless.clock.drivers.display.esp32maskdisplay",
                     { 
                       u"seg_a_pin": 4,
                       u"seg_b_pin": 16,
                       u"seg_c_pin": 5,
                       u"seg_d_pin": 17,
                       u"seg_e_pin": 18,
                       u"seg_f_pin": 13,
                       u"seg_g_pin": 27,
                       u"digit_0_pin": 23,
                       u"digit_1_pin": 19,
                       u"digit_2_pin": 21,
                       u"digit_3_pin": 22,
                       u"brightness_pwm_pin": 26,
                       u"strobe_frequency": 4*60
                    })
    cvars.configure(u"wurthless.clock.drivers.input.gpioinputs",
                     {
                       u"up_pin_id": 25,
                       u"down_pin_id": 33,
                       u"set_pin_id":  32,
                       u"dst_pin_id":  35
                    })

    # not enough CPU time in config mode to run the display
    cvars.set("wurthless.clock.webserver", "disable_display_when_serving", True)

    display = Esp32MaskDisplay(tot)
    if invert_bits is True:
        display = InvertedBitDisplay(display)

    tot.setDisplay( display )
    tot.setInputs( GpioInputs(tot) )
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