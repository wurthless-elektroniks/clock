#
# Defines a TimeSource, e.g., NTP server.
#
class TimeSource:
    '''
    Tries to retrieve UTC time. Returns 0 if unsuccessful, otherwise the UTC timestamp relative to the system's epoch.
    '''
    def getUtcTime(self):
        raise RuntimeError(u"TimeSource.getUtcTime() called directly")
