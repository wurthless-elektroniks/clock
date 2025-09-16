#
# better burn-in script (at last)
#


import time
from wurthless.clock.api.tot import ToT
from wurthless.clock.api.display import DISPLAY_TYPE_NUMERIC, DISPLAY_TYPE_SEVEN_SEGMENT
from wurthless.clock.common.messages import *

def inputTest(tot: ToT):
    display = tot.display()

    display.setBrightness(8)
    while True:
        tot.inputs().strobe()

        up = tot.inputs().up()
        down = tot.inputs().down()
        set = tot.inputs().set()
        dst = tot.inputs().dst()

        # TODO: account for clocks that only populate segs b/c on digit 0
        if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
            button_on  = 0b00000100
            button_off = 0b01011100

            display.setDigitsBinary(button_on if up else button_off,
                                        button_on if down else button_off,
                                        button_on if set else button_off,
                                        button_on if dst else button_off)
        elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
            display.setDigitsNumeric(1 if up else 0,
                                     1 if down else 0,
                                     1 if set else 0,
                                     1 if dst else 0)

        time.sleep(0.1)

# common generic message function test
def burninMessageTest(tot: ToT):
    functions = [
        messagesDisplayCfg,
        messagesDisplayErr,
        messagesDisplayInit,
        messagesDisplayOops,
        messagesDisplaySync,
        messagesDisplayTest
    ]

    for f in functions:
        f(tot.display())
        time.sleep(0.5)

# numeric displays require different burn-in test
def burninNumeric(tot: ToT):
    while True:
        tot.display().setDigitsNumeric(8,8,8,8)
        time.sleep(0.5 * 8)

        # all digits
        for j in range(0,10):
            tot.display().setDigitsNumeric(j,j,j,j)
            time.sleep(0.5)

        # digit 0
        for j in range(0,10):
            tot.display().setDigitsNumeric(j,None,None,None)
            time.sleep(0.5)

        # digit 1
        for j in range(0,10):
            tot.display().setDigitsNumeric(None,j,None,None)
            time.sleep(0.5)
        
        # digit 2
        for j in range(0,10):
            tot.display().setDigitsNumeric(None,None,j,None)
            time.sleep(0.5)
        
        # digit 3
        for j in range(0,10):
            tot.display().setDigitsNumeric(None,None,None,j)
            time.sleep(0.5)

        burninMessageTest(tot)

        tot.display().setDigitsNumeric(8,8,8,8)

        for j in range(0,1):
            for i in range(0,8):
                tot.display().setBrightness(8-i)
                time.sleep(0.5)
            for i in range(0,8):
                tot.display().setBrightness(1+i)
                time.sleep(0.5)

def burninSevenSegment(tot: ToT):
    tot.display().setBrightness(8)

    # "tESt"
    tot.display().setDigitsBinary(0b011111000, 0b01111001, 0b01101101, 0b011111000)

    time.sleep(5)

    while True:
        tot.display().setBrightness(8)
        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        time.sleep(0.5 * 8)

        # segment drives
        for j in range(0,2):
            for i in range(0,7):
                dig = 1 << i
                tot.display().setDigitsBinary(dig,dig,dig,dig)
                time.sleep(0.5)
            tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
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
        for j in range(0,4):
            tot.display().setDigitsBinary(0b01110001, 0b00001110, 0b01110001, 0b00001110)
            time.sleep(0.5)
            tot.display().setDigitsBinary(0b01111000, 0b00000111, 0b01111000, 0b00000111)
            time.sleep(0.5)

        tot.display().setBrightness(8)
        burninMessageTest(tot)

        # brightness test
        tot.display().setDigitsBinary(0x7F, 0x7F, 0x7F, 0x7F)
        for j in range(0,1):
            for i in range(0,8):
                tot.display().setBrightness(8-i)
                time.sleep(0.5)
            for i in range(0,8):
                tot.display().setBrightness(1+i)
                time.sleep(0.5)
   
def burnin(tot: ToT):
    display_type = tot.display().getDisplayType()
    if display_type == DISPLAY_TYPE_NUMERIC:
        burninNumeric(tot)
    elif display_type == DISPLAY_TYPE_SEVEN_SEGMENT:
        burninSevenSegment(tot)