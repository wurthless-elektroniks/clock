'''
Base seven-segment display
'''

from wurthless.clock.api.display import Display, DisplayType
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits

class SevenSegmentDisplay(Display):
    def getDisplayType(self):
        return DisplayType.SEVEN_SEGMENT
    
    def setDigitsNumeric(self, a, b, c, d):
        digs = sevensegNumbersToDigits(a, b, c, d)
        self.setDigitsBinary(digs[0],digs[1],digs[2],digs[3])

