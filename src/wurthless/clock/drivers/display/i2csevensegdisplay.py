'''
Display controlled over I2C
See arduino/ledmux.ino for slave code
'''


from machine import I2C, Pin
from wurthless.clock.drivers.display.sevensegdisplay import SevenSegmentDisplay

# we still have to control PWM; I2C device only strobes digits for us.

class I2CSevenSegmentDisplay(SevenSegmentDisplay):
    def __init__(self):
        self._i2c = I2C(0)
    
    def setDigitsBinary(self, a, b, c, d):
        self._i2c.writeto(0x69, bytes([1, a, b, c, d]))

    def setBrightness(self, brightness):
        pass # TODO
