#
# Decorator for Inputs that waits a specific number of polls before indicating
# that a given button is pressed. Once that delay passes, the button will show
# as pressed for as long as it continues to be held; if the button is released
# at this point the timer will reset.
#
# DebouncedInputs should decorate this class, and not the other way around.
#
from wurthless.clock.api.inputs import Inputs

class DelayedInputButton(object):
    def __init__(self, getter):
        self._delay = 0
        self._getter = getter
        self.reset()

    def reset(self):
        self._ticks = 0
        self._last = False
        self._output = False
        
    def strobe(self):
        state = self._getter()

        if self._last is True and state is True:
            if self._ticks != self._delay:
                self._ticks += 1
            else:
                self._output = True
        else:
            self._output = False
            self._ticks = 0

        self._last = state
        return state

    def output(self):
        return self._output

    def delay(self, delay):
        self._delay = delay

class DelayedInputs(Inputs):
    def __init__(self, inputs):
        self.inputs = inputs
        
        self._up = DelayedInputButton( lambda : self.inputs.up() )
        self._down = DelayedInputButton( lambda : self.inputs.down() )
        self._set = DelayedInputButton( lambda : self.inputs.set() )
        self._dst = DelayedInputButton( lambda : self.inputs.dst() )

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

        # mpy gotcha: true |= False => 1. 
        up = self._up.strobe()
        down = self._down.strobe()
        set = self._set.strobe()
        dst = self._dst.strobe()

        return up or down or set or dst
        
    def up_delay(self, ticks):
        self._up.delay(ticks)
        
    def up(self):
        return self._up.output()
    
    def down_delay(self, ticks):
        self._down.delay(ticks)
        
    def down(self):
        return self._down.output()

    def set_delay(self, ticks):
        self._set.delay(ticks)

    def set(self):
        return self._set.output()

    def dst_delay(self, ticks):
        self._dst.delay(ticks)

    def dst(self):
        return self._dst.output()
    
    def is_dst_dipswitch(self):
        return self.inputs.is_dst_dipswitch()
    