#
# Decorator for other display drivers, that inverts all bits being sent in.
#

from wurthless.clock.api.display import Display

class InvertedBitDisplay(Display):
    def __init__(self, parent):
        self.parent = parent

    def setBrightness(self, brightness):
        self.parent.setBrightness(brightness)

    def setDigitsBinary(self, a, b, c, d):
        self.parent.setDigitsBinary(~a, ~b, ~c, ~d)

    def shutdown(self):
        self.parent.shutdown()