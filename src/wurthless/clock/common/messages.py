'''
Common messages/statuses displayed on the clock.
'''

from wurthless.clock.api.display import Display,DISPLAY_TYPE_NUMERIC,DISPLAY_TYPE_SEVEN_SEGMENT, COLON_STATE_OFF

def _message_display_common(display: Display,
                            seven_segment_data: list,
                            numeric_data: list,
                            colon_state):
    if display.getDisplayType() == DISPLAY_TYPE_SEVEN_SEGMENT:
        display.setDigitsBinary(seven_segment_data[0],
                                seven_segment_data[1],
                                seven_segment_data[2],
                                seven_segment_data[3])
    elif display.getDisplayType() == DISPLAY_TYPE_NUMERIC:
        display.setDigitsNumeric(numeric_data[0],
                                 numeric_data[1],
                                 numeric_data[2],
                                 numeric_data[3])
    display.setColonState(colon_state)

def messagesDisplayInit(display: Display):
    '''
    Displays "INIT", i.e., the clock is starting up.
    '''
    _message_display_common(display,
                            [0b00000110, 0b00110111, 0b00000110, 0b01111000],
                            [8, 8, 8, 8],
                            COLON_STATE_OFF)

def messagesDisplaySync(display: Display):
    '''
    Displays "SYNC", i.e., the clock is trying to synchronize to a timesource.
    '''
    _message_display_common(display,
                        [0b01101101, 0b01101110, 0b00110111, 0b00111001],
                        [9, 9, 9, 9],
                        COLON_STATE_OFF)

def messagesDisplayErr(display: Display):
    '''
    Displays "Err", i.e., an error occurred synchronizing to the timesource.
    '''
    _message_display_common(display,
                    [0, 0b01111001, 0b01010000, 0b01010000],
                    [6, None, 0, 0],
                    COLON_STATE_OFF)

def messagesDisplayOops(display: Display):
    '''
    Displays "Oops", i.e., an exception was thrown in the mainloop.
    '''
    _message_display_common(display,
                [0b01011100,0b01011100,0b01110011,0b01101101],
                [6, None, 9, 9],
                COLON_STATE_OFF)

def messagesDisplayTest(display: Display):
    '''
    Displays "TEST", i.e., the clock is going into test mode.
    '''
    _message_display_common(display,
            [0b011111000, 0b01111001, 0b01101101, 0b011111000],
            [4, None, 9, 9],
            COLON_STATE_OFF)

def messagesDisplayCfg(display: Display):
    '''
    Displays "CFG", i.e., the clock is going into configuration mode.
    '''
    _message_display_common(display,
            [0, 0b00111001, 0b01110001, 0b01111101],
            [4, None, 1, 1],
            COLON_STATE_OFF)

# ------------------------------------------------------------------------------------
#
# Config mode messages
#
# ------------------------------------------------------------------------------------

def messagesDisplaySure(display: Display):
    '''
    Display "SURE" ("are you sure?" message).
    '''
    _message_display_common(display,
        [0b01101101, 0b00111110, 0b01010000, 0b01111001],
        [5, None, 8, 8],
        COLON_STATE_OFF)
    

def messagesDisplayFact(display: Display):
    '''
    Display "fACt" (reset to factory defaults).
    '''
    _message_display_common(display,
        [0b011110001, 0b01110111, 0b00111001, 0b01111000],
        [5, None, 0, 0],
        COLON_STATE_OFF)

def messagesDisplayYes(display: Display):
    _message_display_common(display,
        [0b00000000, 0b01101110, 0b01111001, 0b01101101],
        [None, None, 1, None],
        COLON_STATE_OFF)

def messagesDisplayNo(display: Display):
    _message_display_common(display,
        [0b00000000, 0b01010100, 0b1011100, 0b00000000],
        [None, None, 0, None],
        COLON_STATE_OFF)

def messagesDisplayOn(display: Display):
    _message_display_common(display,
        [0b00000000, 0b1011100, 0b01010100, 0b00000000],
        [None, None, 1, None],
        COLON_STATE_OFF)

def messagesDisplayOff(display: Display):
    _message_display_common(display,
        [0b00000000, 0b1011100, 0b01110001, 0b01110001],
        [None, None, 0, None],
        COLON_STATE_OFF)

def messagesDisplayDone(display: Display):
    _message_display_common(display,
        [0b01011110, 0b1011100, 0b01010100, 0b01111001],
        [5, None, 9, 9],
        COLON_STATE_OFF)

def messagesDisplaySyncMenuItem(display: Display):
    _message_display_common(display,
        [0b01101101, 0b01101110, 0b00110111, 0b00111001],
        [5, None, 0, 1],
        COLON_STATE_OFF)

def messagesDisplayNet(display: Display):
    '''
    Display "NET" (enable/disable networking).
    '''
    _message_display_common(display,
        [0b00000000, 0b01010100, 0b01111001, 0b01111000],
        [5, None, 0, 2],
        COLON_STATE_OFF)
    
def messagesDisplay12Hr(display: Display):
    _message_display_common(display,
        [0b00000110, 0b01011011, 0b01110100, 0b01010000],
        [5, None, 0, 3],
        COLON_STATE_OFF)

def messagesDisplayRoto(display: Display):
    _message_display_common(display,
        [0b01010000, 0b01011100, 0b01111000, 0b01011100],
        [5, None, 0, 4],
        COLON_STATE_OFF)
