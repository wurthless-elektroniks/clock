'''
Generic inputs decorator
'''

from wurthless.clock.api.inputs import Inputs

class DecoratedInputs(Inputs):
    def __init__(self, parent: Inputs):
        self._parent = parent

    def reset(self):
        self._parent.reset()

    def strobe(self) -> bool:
        return self._parent.strobe()

    def up(self) -> bool:
        return self._parent.up()

    def down(self) -> bool:
        return self._parent.down()
    
    def set(self) -> bool:
        return self._parent.set()
    
    def dst(self) -> bool:
        return self._parent.dst()
    
    def is_dst_dipswitch(self) -> bool:
        return self._parent.is_dst_dipswitch()
