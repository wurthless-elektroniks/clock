#
# better burn-in script (at last)
#

import time

def burnin(tot):
    while True:
        tot.display().setBrightness(8)
        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        time.sleep(5)

        for i in range(0,7):
            dig = 1 << i
            tot.display().setDigitsBinary(dig,dig,dig,dig)
            time.sleep(5)

        tot.display().setDigitsBinary(0x7F, 0x00, 0x00, 0x00)
        time.sleep(5)
        tot.display().setDigitsBinary(0x00, 0x7F, 0x00, 0x00)
        time.sleep(5)
        tot.display().setDigitsBinary(0x00, 0x00, 0x7F, 0x00)
        time.sleep(5)
        tot.display().setDigitsBinary(0x00, 0x00, 0x00, 0x7F)
        time.sleep(5)

        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        for i in range(0,8):
            tot.display().setBrightness(8-i)
            time.sleep(5)
        for i in range(0,8):
            tot.display().setBrightness(1+i)
            time.sleep(5)
        