from wurthless.clock.api.rtc import Rtc

class CascadedRtc(Rtc):
    '''
    RTC decorator where we have a "front-end" RTC (typically whatever is on-chip) and a "back-end" RTC (which is battery backed).
    '''
    def __init__(self, frontendRtc, backendRtc):
        self.frontendRtc = frontendRtc
        self.backendRtc = backendRtc

    def getUtcTime(self):
        # frontend time always wins
        ret = self.frontendRtc.getUtcTime()

        # backend RTC should stay synchronized
        self.backendRtc.setUtcTime(ret)

        return ret
    
    def setUtcTime(self, utctime):
        self.frontendRtc.setUtcTime(utctime)
        self.backendRtc.setUtcTime(utctime)
