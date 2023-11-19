#
# Null input driver. Everything returns false.
#
from wurthless.clock.api.inputs import Inputs

class NullInputs(Inputs):
    def __init__(self):
        pass

    def strobe(self):
        pass

    def up(self):
        return False
    
    def down(self):
        return False
    
    def set(self):
        return False

    def dst(self):
        return False
