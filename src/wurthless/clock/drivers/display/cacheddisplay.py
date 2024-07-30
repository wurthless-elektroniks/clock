
from wurthless.clock.api.display import Display

class CachedDisplay(Display):
    def __init__(self, parent):
        self.parent = parent
        self.digits = [ 0, 0, 0, 0 ]

    def setBrightness(self, brightness):
        self.parent.setBrightness(brightness)

    def setDigitsBinary(self, a, b, c, d):
        if self.digits[0] != a or self.digits[1] != b or self.digits[2] != c or self.digits[3] != d:
            self.parent.setDigitsBinary(a,b,c,d)
            self.digits[0] = a
            self.digits[1] = b
            self.digits[2] = c
            self.digits[3] = d

    def shutdown(self):
        self.parent.shutdown()