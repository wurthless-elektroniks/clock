from wurthless.clock.api.nic import Nic
from wurthless.clock.api.rtc import Rtc
from wurthless.clock.api.timesource import TimeSource
from wurthless.clock.api.inputs import Inputs

class ToT(object):
    '''
    Table of Tables, i.e., global state that points to other stuff.
    Platform-specific stuff creates ToT on startup.
    See run_pc.py, run_pico.py, run_esp32.py, etc.
    '''

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

    def nic(self) -> (Nic | None):
        '''
        Return NIC control. see wurthless.clock.api.nic
        '''
        return self._nic

    def setNic(self, nic: Nic):
        self.assertNotFinalized()
        self._nic = nic


    def rtc(self) -> (Rtc | None):
        '''
        Return RTC control. see wurthless.clock.api.rtc
        '''
        return self._rtc

    def setRtc(self, rtc: Rtc):
        self.assertNotFinalized()
        self._rtc = rtc


    def display(self):
        '''
        Return display control. see wurthless.clock.api.display
        '''
        return self._display

    def setDisplay(self, display):
        self.assertNotFinalized()
        self._display = display

    def timesources(self) -> list[TimeSource]:
        '''
        If the clock is configured to synchronize to a known timesource (e.g., NTP, GPS, etc.),
        then return an array of timesources to try to retrieve UTC time from.
        Return empty array otherwise.
        '''
        return self._timesources

    def setTimeSources(self, timesources: list[TimeSource]):
        self.assertNotFinalized()
        self._timesources = timesources

    def inputs(self) -> Inputs:
        '''
        Return input driver. See wurthless.clock.api.inputs
        '''
        return self._inputs

    def setInputs(self, inputs: Inputs):
        self.assertNotFinalized()
        self._inputs = inputs
    
    def cvars(self):
        return self._cvars
    
    def setCvars(self, cvars):
        self.assertNotFinalized()
        self._cvars = cvars

    def finalize(self):
        '''
        Finalize the ToT and prevent software from making further changes to it.
        Should be called before clockmain runs.
        '''
        self.finalized = True
