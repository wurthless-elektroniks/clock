#
# Seven-segment display util functions
#

NUMBERS_TO_DIGITS = [
     0b00111111, # 0
     0b00000110, # 1 
     0b01011011, # 2
     0b01001111, # 3
     0b01100110, # 4
     0b01101101, # 5
     0b01111101, # 6
     0b00000111, # 7
     0b01111111, # 8
     0b01101111  # 9
]

def sevensegNumbersToDigits(segA: (int | None), segB: (int | None), segC: (int | None), segD: (int | None)) -> list[int]:
    '''
    Decode four integers to bitmasks for use with the seven-segment display.
    Each segment value must be between 0 and 9. If out of range, or None, the digit will
    not be populated/displayed (all bits 0).
    '''
    buf = [ 0, 0, 0, 0 ]
    if type(segA) == int and 0 <= segA and segA <= 9:
        buf[0] = NUMBERS_TO_DIGITS[segA]
    else:
        buf[0] = 0
    
    if type(segB) == int and 0 <= segB and segB <= 9:
        buf[1] = NUMBERS_TO_DIGITS[segB]
    else:
        buf[1] = 0
    
    if type(segC) == int and 0 <= segC and segC <= 9:
        buf[2] = NUMBERS_TO_DIGITS[segC]
    else:
        buf[2] = 0
    
    if type(segD) == int and 0 <= segD and segD <= 9:
        buf[3] = NUMBERS_TO_DIGITS[segD]
    else:
        buf[3] = 0
    return buf
