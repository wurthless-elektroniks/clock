from threading import Thread, Lock
from time import sleep
from wurthless.clock.api.rtc import Rtc

def _thunk(rtc):
    rtc._thread()

class SoftRtc(Rtc):
    '''
    Software (i.e., very unreliable) RTC.
    To be used only during testing. Use Python3Rtc or MicropythonRTC.
    '''
    def __init__(self):
        self.time = 0
        self.threadinstance = None
        self.mutex = Lock()

    def _thread(self):
        while True:
            with self.mutex:
                self.time += 1
            sleep(1)

    def isUp(self):
        # return true if thread is running
        return self.threadinstance is not None and self.threadinstance.is_alive()

    def getUtcTime(self):
        with self.mutex:
            # if thread not running, return 0 always
            if self.isUp() is False:
                return 0
            return self.time
    
    def setUtcTime(self, timestamp):
        with self.mutex:
            self.time = timestamp

            # if thread not running, start it.
            if self.isUp() is False:
                self.threadinstance = Thread(target=_thunk, args=[self])
                self.threadinstance.start()
