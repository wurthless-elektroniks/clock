#
# Interface on to RTC.
#
# This only handles the storage and retrieval of current time settings.
# DST / timezone control are to be done elsewhere.
#
class Rtc:
    '''
    Returns true if the RTC was successfully set.
    
    This will return False if:
    - on battery backed RTCs, the RTC is not in an initialized state (first powerup, or battery had died)
    '''
    def isUp(self):
        return False

    def getUtcTime(self):
        return 0

    def setUtcTime(self):
        pass

    '''
    Return True if it's not possible to change the time.
    '''
    def readOnly(self):
        return False

