#
# Fast-ish baremetal driver for ESP32 inputs.
# Mostly done so that input polling doesn't have to go through micropython abstractions.
#

from wurthless.clock.api.inputs import Inputs
from machine import Pin,mem32
from wurthless.clock.cvars.cvars import registerCvar

registerCvar(u"wurthless.clock.drivers.input.esp32gpioinputs", u"up_pin_id",    u"Int", u"GPIO pin for UP button.", 25)
registerCvar(u"wurthless.clock.drivers.input.esp32gpioinputs", u"down_pin_id",  u"Int", u"GPIO pin for DOWN button.", 33)
registerCvar(u"wurthless.clock.drivers.input.esp32gpioinputs", u"set_pin_id",   u"Int", u"GPIO pin for SET button.", 32)
registerCvar(u"wurthless.clock.drivers.input.esp32gpioinputs", u"dst_pin_id",   u"Int", u"GPIO pin for DST button.", 35)

GPIO_IN_REG  = 0x3FF4403C
GPIO_IN1_REG = 0x3FF44040

class Esp32GpioInputs(Inputs):
    def __init__(self, tot):


        # let micropython configure the I/O matrix
        up_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.esp32gpioinputs", u"up_pin_id")
        down_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.esp32gpioinputs", u"down_pin_id")
        set_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.esp32gpioinputs", u"set_pin_id")
        dst_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.esp32gpioinputs", u"dst_pin_id")
        Pin(up_pin_id, Pin.IN, Pin.PULL_UP)
        Pin(down_pin_id, Pin.IN, Pin.PULL_UP)
        Pin(set_pin_id, Pin.IN, Pin.PULL_UP)
        Pin(dst_pin_id, Pin.IN, Pin.PULL_UP)

        self.in_data = 0
        self.in1_data = 0
        
        # build andmasks
        self.in_mask = 0
        self.in1_mask = 0
        for i in [ up_pin_id, down_pin_id, set_pin_id, dst_pin_id ]:
            if i >= 32:
                self.in1_mask |= (1 << (i-32))
            else:
                self.in_mask |= (1 << i)

        # configure lambdas for each
        self.up_pressed_callback = self.make_lambda(up_pin_id)
        self.down_pressed_callback = self.make_lambda(down_pin_id)
        self.set_pressed_callback = self.make_lambda(set_pin_id)
        self.dst_pressed_callback = self.make_lambda(dst_pin_id)

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
