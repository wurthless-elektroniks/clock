

class Inputs(object):
    '''
    Interface to the input device. The input device defines four buttons (up, down, set, DST).
    '''
    
    def reset(self):
        '''
        Reset input device driver to a known state.
        If the driver expects to have inputs latched/debounced, it should reset that logic.
        '''
        pass

    def strobe(self):
        '''
        Read inputs. Button states are only updated when this function is called. At all other times,
        they return the results of the last strobe.
        '''
        pass

    def up(self) -> bool:
        '''
        Return True if up button pressed.
        '''
        return False
    

    def down(self) -> bool:
        '''
        Return True if down button pressed.
        '''
        return False
    
    def set(self) -> bool:
        '''
        Return True if set button pressed.
        '''
        return False
    
    def dst(self) -> bool:
        '''
        Return True if DST button pressed.
        '''
        return False
    
