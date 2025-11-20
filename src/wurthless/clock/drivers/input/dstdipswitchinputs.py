
from wurthless.clock.api.inputs import Inputs

class DstDipswitchInputs(Inputs):
    def __init__(self, inputs):
        self._inputs = inputs

    def reset(self):
        self._inputs.reset()

    def is_dst_dipswitch(self):
        return True

    def strobe(self):
        if self._inputs.strobe() is False:
            return False

        # strobe() ignores DST
        return self._inputs.up() or self._inputs.down() or self._inputs.set()

    def up(self):
        return self._inputs.up()

    def down(self):
        return self._inputs.down()

    def set(self):
        return self._inputs.set()

    def dst(self):
        return self._inputs.dst()
