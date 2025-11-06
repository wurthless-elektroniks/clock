


# micropython does NOT support enum!!
DISPLAY_TYPE_SEVEN_SEGMENT = 0
DISPLAY_TYPE_NUMERIC       = 1


COLON_STATE_OFF   = 0
COLON_STATE_ON    = 1
COLON_STATE_BLINK = 2

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

    def setColonState(self, colon_state: int):
        '''
        Changes colon state, if the display has a colon. Does nothing otherwise.

        Parameters:
        - colon_state: New state. Can be one of COLON_STATE_OFF (turns colon off),
          COLON_STATE_ON (turns colon on), or COLON_STATE_BLINK (blinks the colon at 2 Hz).
        '''
        pass