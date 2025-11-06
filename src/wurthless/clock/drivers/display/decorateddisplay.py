'''
Base display decorator class.
'''

from wurthless.clock.api.display import Display

class DecoratedDisplay(Display):
    def __init__(self, parent):
        self._parent = parent

    def setBrightness(self, brightness: int):
        self._parent.setBrightness(brightness)

    def getDisplayType(self):
        return self._parent.getDisplayType()

    def blank(self):
        self._parent.blank()

    def setDigitsNumeric(self, a: int | None, b: int | None, c: int | None, d: int | None):
        self._parent.setDigitsNumeric(a,b,c,d)
        
    def setDigitsBinary(self, a: int, b: int, c: int, d: int):
        self._parent.setDigitsBinary(a,b,c,d)

    def shutdown(self):
        self._parent.shutdown()

    def setColonState(self, colon_state: int):
        self._parent.setColonState(colon_state)
