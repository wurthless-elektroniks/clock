'''
Base seven-segment display
'''

from wurthless.clock.api.display import Display, DISPLAY_TYPE_SEVEN_SEGMENT
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits

class SevenSegmentDisplay(Display):
    def getDisplayType(self):
        return DISPLAY_TYPE_SEVEN_SEGMENT
    
    def setDigitsNumeric(self, a, b, c, d):
        digs = sevensegNumbersToDigits(a, b, c, d)
        self.setDigitsBinary(digs[0],digs[1],digs[2],digs[3])

