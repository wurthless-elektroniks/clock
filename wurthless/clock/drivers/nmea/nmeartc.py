#
# NMEA device as RTC
#
# This doesn't return particularly accurate results, so it's best to cascade to another RTC.
#

from wurthless.clock.api.rtc import Rtc

class NmeaRtc(Rtc):
    def __init__(self, nmeadev):
        self.nmeadev = nmeadev

    def isUp(self):
        return self.nmeadev.isUp()
    
    def getUtcTime(self):
        return self.nmeadev.getUtcTime()

    def setUtcTime(self, utctime):
        # not possible to set time
        pass
