#
# Default RTC provided by Micropython. Can be hardware- or software-based. We don't care as long as it keeps time.
#

import time
from machine import RTC
from wurthless.clock.api.rtc import Rtc
from wurthless.clock.common.timestamp import timeTupleToTimestamp, timestampToTimeTuple

class MicropythonRTC(Rtc):
    def __init__(self):
        self.rtc = RTC()
    
    def isUp(self):
        # any year before 2022 assumed to be bad
        return self.rtc.datetime()[0] >= 2022

    def getUtcTime(self):
        rtcdt = self.rtc.datetime()

        # RTC does not work on the standard python time struct. we fix that here
        pydt = ( rtcdt[0], rtcdt[1], rtcdt[2], rtcdt[4], rtcdt[5], rtcdt[6], 0, 0, 0 )

        return timeTupleToTimestamp(pydt)
    
    def setUtcTime(self, timestamp):
        pydt = timestampToTimeTuple(timestamp)

        self.rtc.datetime( (pydt[0], pydt[1], pydt[2], 0, pydt[3], pydt[4], pydt[5], 0) )
