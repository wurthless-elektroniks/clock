

class Inputs:
    def reset(self):
        '''
        Reset input device driver to a known state.
        If the driver expects to have inputs latched/debounced, it should reset that logic.
        '''
        pass


    def strobe(self):
        '''
        Read inputs. Values of the below functions are not to change until strobe() is called again.
        '''
        pass

    def up(self):
        '''
        Return True if up button pressed.
        '''
        return False
    

    def down(self):
        '''
        Return True if down button pressed.
        '''
        return False
    
    def set(self):
        '''
        Return True if set button pressed.
        '''
        return False
    
    def dst(self):
        '''
        Return True if DST button pressed.
        '''
        return False
    
