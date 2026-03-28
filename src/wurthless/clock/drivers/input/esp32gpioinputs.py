#
# Fast-ish baremetal driver for ESP32 inputs.
# Mostly done so that input polling doesn't have to go through micropython abstractions.
#

from wurthless.clock.api.inputs import Inputs
from machine import Pin,mem32

# cvars are not used here to try to save memory
UP_PIN_ID   = 25
DOWN_PIN_ID = 33
SET_PIN_ID  = 32
DST_PIN_ID  = 35

GPIO_IN_REG  = 0x3FF4403C
GPIO_IN1_REG = 0x3FF44040

class Esp32GpioInputs(Inputs):
    def __init__(self, tot):
        # let micropython configure the I/O matrix
        Pin(UP_PIN_ID, Pin.IN, Pin.PULL_UP)
        Pin(DOWN_PIN_ID, Pin.IN, Pin.PULL_UP)
        Pin(SET_PIN_ID, Pin.IN, Pin.PULL_UP)
        Pin(DST_PIN_ID, Pin.IN, Pin.PULL_UP)

        self.in_data = 0
        self.in1_data = 0
        
        # build andmasks
        self.in_mask = 0
        self.in1_mask = 0
        for i in [ UP_PIN_ID, DOWN_PIN_ID, SET_PIN_ID, DST_PIN_ID ]:
            if i >= 32:
                self.in1_mask |= (1 << (i-32))
            else:
                self.in_mask |= (1 << i)

        # configure lambdas for each
        self.up_pressed_callback = self.make_lambda(UP_PIN_ID)
        self.down_pressed_callback = self.make_lambda(DOWN_PIN_ID)
        self.set_pressed_callback = self.make_lambda(SET_PIN_ID)
        self.dst_pressed_callback = self.make_lambda(DST_PIN_ID)

    def make_lambda(self, pin):
        if pin >= 32:
            return lambda: (self.in1_data & (1<<(pin-32))) != 0
        else:
            return lambda: (self.in_data & (1<<pin)) != 0
    
    def strobe(self):
        self.in_data  = ~mem32[GPIO_IN_REG] & self.in_mask
        self.in1_data = ~mem32[GPIO_IN1_REG] & self.in1_mask
        return self.in_data != 0 or self.in1_data != 0

    def up(self):
        return self.up_pressed_callback()
    
    def down(self):
        return self.down_pressed_callback()
    
    def set(self):
        return self.set_pressed_callback()

    def dst(self):
        return self.dst_pressed_callback()
