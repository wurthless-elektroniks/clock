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

    if curses.can_change_color():
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)  
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)  
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)  
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)  
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)  
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)  
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN) 
        
    # platform initialization
    tot = ToT()

    cvars = Cvars()
    writer = TokenedCvarWriter()
    writer.addPreflight(u"secrets/factory.ini")
    cvars.setWriter(writer)
    cvars.load()
    tot.setCvars( cvars )

    tot.cvars().set(u"wurthless.clock.clockmain", u"set_and_dst_no_debounce", True)

    # settings writeback delay would ideally be 0 seconds, but we make it 60 so it's easier to tell that there is a delay.
    tot.cvars().set(u"wurthless.clock.clockmain", u"settings_write_delay", 60)

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

    if u"-burnin" in sys.argv:
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_burnin", True)

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
