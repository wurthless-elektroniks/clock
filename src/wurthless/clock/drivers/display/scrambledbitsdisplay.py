'''
Decorator for RP2040-based boards where the PIO output bits are reversed
or otherwise scrambled.
'''

from wurthless.clock.api.display import Display
from wurthless.clock.drivers.display.decorateddisplay import DecoratedDisplay
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits

REVERSED_BITS_MAPPING = {
    6: 0,
    5: 1,
    4: 2,
    3: 3,
    2: 4,
    1: 5,
    0: 6
}

class ScrambledBitsDisplay(DecoratedDisplay):
    def __init__(self, parent, bit_mappings: dict):
        super().__init__(parent)
        self._bit_mappings = bit_mappings

    def _bitswap(self, bits):
        result = 0
        for bit_in, bit_out in self._bit_mappings.items():
            result |= 1 << bit_out if (bits & (1 << bit_in)) != 0 else 0
        return result
    
    def setDigitsNumeric(self, a, b, c, d):
        a_segs, b_segs, c_segs, d_segs = sevensegNumbersToDigits(a, b, c, d)
        self.setDigitsBinary(a_segs,b_segs,c_segs,d_segs)

    def setDigitsBinary(self, a, b, c, d):
        swapped_a = self._bitswap(a)
        swapped_b = self._bitswap(b)
        swapped_c = self._bitswap(c)
        swapped_d = self._bitswap(d)

        super().setDigitsBinary(swapped_a, swapped_b, swapped_c, swapped_d)
