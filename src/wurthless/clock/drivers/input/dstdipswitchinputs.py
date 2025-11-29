
from wurthless.clock.drivers.input.decoratedinputs import DecoratedInputs
class DstDipswitchInputs(DecoratedInputs):
    def is_dst_dipswitch(self):
        return True

    def strobe(self):
        if super().strobe() is False:
            return False

        # strobe() ignores DST
        return self.up() or self.down() or self.set()
