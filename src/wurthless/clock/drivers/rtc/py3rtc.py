#
# Standard Python3 time wrapped as an Rtc instance.
# Not possible to change this clock at all.
#

import time
from wurthless.clock.common.timestamp import timeTupleToTimestamp
from wurthless.clock.api.rtc import Rtc

class Python3Rtc(Rtc):
    def __init__(self):
        pass

    def isUp(self):
        return True
        
    def getUtcTime(self):
        return timeTupleToTimestamp(time.gmtime())
    
    def setUtcTime(self, timestamp):
        # can't change the system time
        pass

    def readOnly(self):
        return True
