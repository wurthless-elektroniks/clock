#
# Table of Tables, i.e., global state that points to other stuff.
# Platform-specific stuff creates ToT on startup. See run_pc.py or run_pico.py
#

class ToT:
    def __init__(self):
        self._finalized = False
        self._nic = None
        self._rtc = None
        self._display = None
        self._timesources = []
        self._inputs = None
        self._cvars = None

    def assertNotFinalized(self):
        if self._finalized is True:
            raise RuntimeError(u"this ToT is finalized")

    '''
    Return NIC control. see wurthless.clock.api.nic
    '''
    def nic(self):
        return self._nic

    def setNic(self, nic):
        self.assertNotFinalized()
        self._nic = nic

    '''
    Return RTC control. see wurthless.clock.api.rtc
    '''
    def rtc(self):
        return self._rtc

    def setRtc(self, rtc):
        self.assertNotFinalized()
        self._rtc = rtc

    '''
    Return display control. see wurthless.clock.api.display
    '''
    def display(self):
        return self._display

    def setDisplay(self, display):
        self.assertNotFinalized()
        self._display = display

    '''
    If the clock is configured to synchronize to a known timesource (e.g., NTP, GPS, etc.),
    then return an array of timesources to try to retrieve UTC time from.
    Return empty array otherwise.
    '''
    def timesources(self):
        return self._timesources

    def setTimeSources(self, timesources):
        self.assertNotFinalized()
        self._timesources = timesources

    def inputs(self):
        return self._inputs

    def setInputs(self, inputs):
        self.assertNotFinalized()
        self._inputs = inputs
    
    def cvars(self):
        return self._cvars
    
    def setCvars(self, cvars):
        self.assertNotFinalized()
        self._cvars = cvars

    def finalize(self):
        self.finalized = True
