class Rtc(object):
    '''
    Interface to a RTC device. Only handles storage/retrieval of UTC time,
    timezone/DST control are to be handled in software.
    '''

    def isUp(self) -> bool:
        '''
        Returns true if the RTC was successfully set and is currently running.
        If False, the RTC hasn't been initialized yet, or has stopped running (e.g., battery-backed RTC's battery has died).
        '''
        return False

    def getUtcTime(self) -> int:
        '''
        Return current UTC time relative to the system's epoch. If 0, the RTC is not initialized.
        '''
        return 0

    def setUtcTime(self, timestamp: int):
        '''
        Set UTC time. If the RTC is read only, undefined behavior results.
        '''
        pass

    def readOnly(self) -> bool:
        '''
        Return True if it's not possible to change the time.
        '''
        return False

