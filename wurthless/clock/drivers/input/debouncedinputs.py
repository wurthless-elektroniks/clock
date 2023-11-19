#
# Wrapper for an input device that auto-debounces input.
# Basically, if we see that any of our inputs are pressed two times in a row,
# we will return False for them.
#

from wurthless.clock.api.inputs import Inputs

class DebouncedInputs(Inputs):
    def __init__(self, inputs):
        self.inputs = inputs
        self._up_last = False
        self._down_last = False
        self._set_last = False
        self._dst_last = False
    
        self._up_current = False
        self._down_current = False
        self._set_current = False
        self._dst_current = False

    def strobe(self):
        # rotate "current" inputs to last poll
        self._up_last   = self._up_current
        self._down_last = self._down_current
        self._set_last  = self._set_current
        self._dst_last  = self._dst_current
        
        self.inputs.strobe()

        self._up_current    = self.inputs.up()
        self._down_current  = self.inputs.down()
        self._set_current   = self.inputs.set()
        self._dst_current   = self.inputs.down()
    
    def up(self):
        return self._up_last is False and self._up_current is True
    
    def down(self):
        return self._down_last is False and self._down_current is True
    
    def set(self):
        return self._set_last is False and self._set_current is True
    
    def dst(self):
        return self._dst_last is False and self._dst_current is True
