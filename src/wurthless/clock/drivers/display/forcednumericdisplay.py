'''
Decorator for seven-segment display that forces callers to treat it like a numeric display.
Used for testing.
'''

from wurthless.clock.api.display import Display,DisplayType

class ForcedNumericDisplay(Display):
    def __init__(self, parent):
        self._parent = parent

    def getDisplayType(self):
        return DisplayType.NUMERIC
    
    def setBrightness(self, brightness):
        self._parent.setBrightness(brightness)
    
    def setDigitsNumeric(self, a, b, c, d):
        self._parent.setDigitsNumeric(a,b,c,d)

    def shutdown(self):
        self._parent.shutdown()
