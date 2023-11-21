from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.display.ioseqdisplay import IoseqDisplay
from wurthless.clock.mock.nullinputs import NullInputs
from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic

from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter

import config


def boot_display():
    tot = ToT()
    cvars = Cvars()
    tot.setCvars( cvars )

    print(u"init/return display...")
    return IoseqDisplay(tot)

