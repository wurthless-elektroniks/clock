class Display(object):
    '''
    Interface to a seven-segment display device.
    '''
        
    def setBrightness(self, brightness: int):
        '''
        Set brightness to a value between 1 and 8. If the device doesn't support brightness, this does nothing.
        '''
        pass


    def setDigitsBinary(self, a: int, b: int, c: int, d: int):
        '''
        Set digits on seven-segment display manually using binary bitmasks (LSB = segment A).
        '''
        pass

    def shutdown(self):
        '''
        Permanently shuts down the display driver. A reboot is necessary to restart it.
        '''
        pass