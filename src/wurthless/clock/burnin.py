#
# better burn-in script (at last)
#


import time
from wurthless.clock.api.tot import ToT

def inputTest(tot: ToT):
    tot.display().setBrightness(8)
    while True:
        tot.inputs().strobe()

        up = tot.inputs().up()
        down = tot.inputs().down()
        set = tot.inputs().set()
        dst = tot.inputs().dst()

        # TODO: account for clocks that only populate segs b/c on digit 0
        button_on  = 0b00000100 
        button_off = 0b01011100

        tot.display().setDigitsBinary(button_on if up else button_off,
                                      button_on if down else button_off,
                                      button_on if set else button_off,
                                      button_on if dst else button_off)

        time.sleep(0.1)

def burnin(tot: ToT):
    while True:
        tot.display().setBrightness(8)
        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        time.sleep(5)

        # segment drives
        for j in range(0,2):
            for i in range(0,7):
                dig = 1 << i
                tot.display().setDigitsBinary(dig,dig,dig,dig)
                time.sleep(0.5)

        # digit drives
        for j in range(0,4):
            tot.display().setDigitsBinary(0x7F, 0x00, 0x00, 0x00)
            time.sleep(0.5)
            tot.display().setDigitsBinary(0x00, 0x7F, 0x00, 0x00)
            time.sleep(0.5)
            tot.display().setDigitsBinary(0x00, 0x00, 0x7F, 0x00)
            time.sleep(0.5)
            tot.display().setDigitsBinary(0x00, 0x00, 0x00, 0x7F)
            time.sleep(0.5)
     
        # anti-ghosting test (bad LEDs cause bleedovers)
        # has to run at lowest brightness because that's when the problem is most obvious
        tot.display().setBrightness(1)
        for j in range(0,4):
            tot.display().setDigitsBinary(0b01001001, 0b00110110, 0b01001001, 0b00110110)
            time.sleep(0.5)
            tot.display().setDigitsBinary(0b00110110, 0b01001001, 0b00110110, 0b01001001)
            time.sleep(0.5)

        # brightness test
        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        for j in range(0,1):
            for i in range(0,8):
                tot.display().setBrightness(8-i)
                time.sleep(0.5)
            for i in range(0,8):
                tot.display().setBrightness(1+i)
                time.sleep(0.5)
   