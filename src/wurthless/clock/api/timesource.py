
TIMESOURCE_GENERIC_ERROR = 0
"""
Timesource couldn't return time for whatever reason. Try again later.
"""

TIMESOURCE_MUST_FORGET   = -1
"""
Timesource explicitly told us to not connect to it anymore.
"""

TIMESOURCE_RATE_LIMIT    = -2
"""
Timesource has rate limited us. Caller must decrease polling interval and continue to
decrease it upon receiving another rate limit error.
"""

class TimeSource(object):
    '''
    Interface to a time source, such as an NTP server, GPS device, WWVB receiver, etc.
    '''

    def getUtcTime(self) -> int:
        '''
        On success, return UTC time relative to system epoch.

        Any value of 0 or less is to be treated as an error
        (see TIMESOURCE_GENERIC_ERROR, TIMESOURCE_MUST_FORGET, TIMESOURCE_RATE_LIMIT)
        '''
        raise RuntimeError(u"TimeSource.getUtcTime() called directly")
