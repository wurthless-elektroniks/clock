from wurthless.clock.api.timesource import TimeSource

class NmeaTimeSource(TimeSource):
    def __init__(self, nmeadev):
        self.nmeadev = nmeadev

    def getUtcTime(self):
        return self.nmeadev.getUtcTime()
