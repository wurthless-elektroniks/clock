class TimeSource(object):
    '''
    Interface to a time source, such as an NTP server, GPS device, WWVB receiver, etc.
    '''

    def getUtcTime(self) -> int:
        '''
        Tries to retrieve UTC time. Returns 0 if unsuccessful, otherwise the UTC timestamp relative to the system's epoch.
        '''
        raise RuntimeError(u"TimeSource.getUtcTime() called directly")
