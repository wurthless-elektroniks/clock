from wurthless.clock.api.inputs import Inputs

class NullInputs(Inputs):
    '''
     Null input driver. Everything returns false.
    '''
    def __init__(self):
        pass

    def strobe(self):
        return False

    def up(self):
        return False
    
    def down(self):
        return False
    
    def set(self):
        return False

    def dst(self):
        return False
