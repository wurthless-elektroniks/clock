#
# Run TMUCITW on desktop.
#

import sys
import curses

from wurthless.clock.api.tot import ToT
from wurthless.clock.clockmain import clockMain

from wurthless.clock.mock.cursesdisplay import CursesDisplay
from wurthless.clock.mock.cursesinputs import CursesInputs
from wurthless.clock.cvars.cvars import Cvars
from wurthless.clock.cvars.cvarwriter import TokenedCvarWriter


from wurthless.clock.common.ntp import NtpTimeSource

from wurthless.clock.drivers.nic.stubnic import StubNic
from wurthless.clock.drivers.rtc.py3rtc import Python3Rtc
from wurthless.clock.drivers.rtc.softrtc import SoftRtc

# must-init cvars must be defined, so don't remove this
import config

def args():
    print(u"""
the most useless clock in the world emulator/mockup

i demand arguments be passed because real hardware configurations can be messy
and we need to test all possible configurations.

script usage: python3 run_pc.py [scenario] -go

By default, clock uses current system time and is only reconfigurable by adjusting cvars.

Scenario is one of the following:
-softrtc: Initialize with fake software RTC and no timesources set.
-ntp: Initialize with fake software RTC, wrap system nic
-server: Startup in server mode. Software will listen on port 80. (Microdot is required to run this!)
                    
you need to specify -go in the arguments list or else this thing won't start and you'll
get this message.

pycurses must be present for this emulator to work at all.
    """)

def cursesMain(stdscr):
    # input driver requires it
    stdscr.nodelay(True)

    # platform initialization
    tot = ToT()

    cvars = Cvars()
    writer = TokenedCvarWriter()
    cvars.setWriter(writer)
    cvars.load()
    tot.setCvars( cvars )

    tot.cvars().set(u"wurthless.clock.clockmain", u"set_and_dst_no_debounce", True)

    tot.setDisplay( CursesDisplay(stdscr) )
    tot.setInputs( CursesInputs(stdscr) )

    if u"-ntp" in sys.argv or u"-server" in sys.argv:
        tot.setNic( StubNic() )
        tot.setTimeSources( [ NtpTimeSource(tot) ] )
    else:
        tot.setTimeSources( [] )

    if u"-softrtc" in sys.argv or u"-ntp" in sys.argv:
        softrtc = SoftRtc()
        tot.setRtc( softrtc )
    else:
        tot.setRtc( Python3Rtc() )

    if u"-server" in sys.argv:
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()

    # go to it
    clockMain(tot)
    
def main():
    if len(sys.argv) < 2:
        args()
        return

    # scan for -go as that's the only thing that we need to start the thing
    go = False
    for i in sys.argv:
        if i == u"-go":
            go = True

    if go is False:
        args()
        return

    curses.wrapper(cursesMain)

main()
