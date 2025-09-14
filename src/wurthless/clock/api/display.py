from enum import Enum

class DisplayType(Enum):
    SEVEN_SEGMENT = 0
    
    NUMERIC = 1

class Display(object):
    '''
    Interface to a seven-segment display device.
    '''
        
    def setBrightness(self, brightness: int):
        '''
        Set brightness to a value between 1 and 8. If the device doesn't support brightness, this does nothing.
        '''
        raise RuntimeError("unimplemented")

    def getDisplayType(self):
        raise RuntimeError("unimplemented")

    def blank(self):
        '''
        Blanks the display.
        '''
        self.setDigitsNumeric(None, None, None, None)

    def setDigitsNumeric(self, a: int | None, b: int | None, c: int | None, d: int | None):
        raise RuntimeError("unimplemented")

    def setDigitsBinary(self, a: int, b: int, c: int, d: int):
        '''
        Set digits on seven-segment display manually using binary bitmasks (LSB = segment A).
        If this is not a seven-segment display, an exception will be thrown.
        Call getDisplayType() first.
        '''
        raise RuntimeError("unimplemented")

    def shutdown(self):
        '''
        Permanently shuts down the display driver. A reboot is necessary to restart it.
        '''
        pass