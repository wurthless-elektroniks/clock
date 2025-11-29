from wurthless.clock.api.display import Display
from wurthless.clock.drivers.display.decorateddisplay import DecoratedDisplay

class ReversedDigitsDisplay(DecoratedDisplay):
    def __init__(self, parent):
        super().__init__(parent)

    def setDigitsNumeric(self, a, b, c, d):
        super().setDigitsNumeric(d, c, b, a)
    
    def setDigitsBinary(self, a, b, c, d):
        super().setDigitsBinary(d, c, b, a)
