#
# Seven-segment display control
# 


class Display:
    def setBrightness(self, brightness):
        pass

    '''
    Set digits on seven-segment display manually using binary bitmasks (LSB = segment A).
    '''
    def setDigitsBinary(self, a, b, c, d):
        pass

    '''
    Permanently shuts down the display driver. A reboot is necessary to restart it.
    '''
    def shutdown(self):
        pass