#
# Wrapper for an input device that auto-debounces input.
# Basically, if we see that any of our inputs are pressed two times in a row,
# we will return False for them.
#

from wurthless.clock.api.inputs import Inputs

class DebouncedInputButton(object):
    def __init__(self, getter):
        self._getter = getter
        self.reset()

    def reset(self):
        self._last = False
        self._output = False

    def strobe(self):
        self._last = self._output
        self._output = self._getter()
        return self._output
    
    def output(self):
        return self._last is False and self._output is True

class DebouncedInputs(Inputs):
    def __init__(self, inputs):
        self.inputs = inputs
        self._up = DebouncedInputButton( lambda : self.inputs.up() )
        self._down = DebouncedInputButton( lambda : self.inputs.down() )
        self._set = DebouncedInputButton( lambda : self.inputs.set() )
        self._dst = DebouncedInputButton( lambda : self.inputs.dst() )
    
    def reset(self):
        self._up.reset()
        self._down.reset()
        self._set.reset()
        self._dst.reset()
        
        self.inputs.reset()

    def strobe(self):
        if self.inputs.strobe() is False:
            self._up.reset()
            self._down.reset()
            self._set.reset()
            self._dst.reset()
            return False

        # mpy gotcha: true |= False => 1, and not True as we'd expect
        up = self._up.strobe()
        down = self._down.strobe()
        set = self._set.strobe()
        dst = self._dst.strobe()
        
        return up or down or set or dst

    def up(self):
        return self._up.output()
    
    def down(self):
        return self._down.output()
    
    def set(self):
        return self._set.output()
    
    def dst(self):
        return self._dst.output()
