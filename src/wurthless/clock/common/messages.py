'''
Common messages/statuses displayed on the clock.
'''

from wurthless.clock.api.display import Display,DISPLAY_TYPE_NUMERIC,DISPLAY_TYPE_SEVEN_SEGMENT

def messagesDisplayInit(display: Display):
    '''
    Displays "INIT", i.e., the clock is starting up.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0b00000110, 0b00110111, 0b00000110, 0b01111000)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(8, 8, 8, 8)

def messagesDisplaySync(display: Display):
    '''
    Displays "SYNC", i.e., the clock is trying to synchronize to a timesource.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0b01101101, 0b01101110, 0b00110111, 0b00111001)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(9, 9, 9, 9)

def messagesDisplayErr(display: Display):
    '''
    Displays "Err", i.e., an error occurred synchronizing to the timesource.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0, 0b01111001, 0b01010000, 0b01010000)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(6, None, 0, 0)

def messagesDisplayOops(display: Display):
    '''
    Displays "Oops", i.e., an exception was thrown in the mainloop.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0b01011100,0b01011100,0b01110011,0b01101101)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(6, None, 9, 9)

def messagesDisplayTest(display: Display):
    '''
    Displays "TEST", i.e., the clock is going into test mode.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0b011111000, 0b01111001, 0b01101101, 0b011111000)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(4, None, 9, 9)

def messagesDisplayCfg(display: Display):
    '''
    Displays "CFG", i.e., the clock is going into configuration mode.
    '''
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(0, 0b00111001, 0b01110001, 0b01111101)
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(4, None, 1, 1)
