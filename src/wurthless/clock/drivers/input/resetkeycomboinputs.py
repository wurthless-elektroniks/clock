'''
Force hard reset on three-fingered salute (UP/DOWN/SET pressed simultaneously).

Needed for boards that don't have a dedicated reset button.
'''

import machine
from wurthless.clock.drivers.input.decoratedinputs import DecoratedInputs

class ResetKeycomboInputs(DecoratedInputs):
    def strobe(self):
        if self.up() and self.down() and self.set():
            machine.reset()

        return super().strobe()
