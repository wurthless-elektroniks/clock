#
# GPIO interface via Micropython. All pins assumed active low.
#
from wurthless.clock.api.inputs import Inputs
from machine import Pin

from wurthless.clock.cvars.cvars import registerCvar

# Cvars - these assume RPi Pico-based hardware
registerCvar(u"wurthless.clock.drivers.input.gpioinputs", u"up_pin_id",    u"Int", u"GPIO pin for UP button.", 7)
registerCvar(u"wurthless.clock.drivers.input.gpioinputs", u"down_pin_id",  u"Int", u"GPIO pin for DOWN button.", 8)
registerCvar(u"wurthless.clock.drivers.input.gpioinputs", u"set_pin_id",   u"Int", u"GPIO pin for SET button.", 9)
registerCvar(u"wurthless.clock.drivers.input.gpioinputs", u"dst_pin_id",   u"Int", u"GPIO pin for DST button.", 11)

class GpioInputs(Inputs):
    def __init__(self, tot):
        up_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.gpioinputs", u"up_pin_id")
        down_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.gpioinputs", u"down_pin_id")
        set_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.gpioinputs", u"set_pin_id")
        dst_pin_id = tot.cvars().get(u"wurthless.clock.drivers.input.gpioinputs", u"dst_pin_id")

        self.up_pin = Pin(up_pin_id, Pin.IN, Pin.PULL_UP)
        self.down_pin = Pin(down_pin_id, Pin.IN, Pin.PULL_UP)
        self.set_pin = Pin(set_pin_id, Pin.IN, Pin.PULL_UP)
        self.dst_pin = Pin(dst_pin_id, Pin.IN, Pin.PULL_UP)

        self.up_pressed   = False
        self.down_pressed = False
        self.set_pressed  = False
        self.dst_pressed  = False
    
    def strobe(self):
        self.up_pressed   = self.up_pin.value() == 0
        self.down_pressed = self.down_pin.value() == 0
        self.set_pressed  = self.set_pin.value() == 0
        self.dst_pressed  = self.dst_pin.value() == 0
        return self.up_pressed or self.down_pressed or self.set_pressed or self.dst_pressed

    def up(self):
        return self.up_pressed
    
    def down(self):
        return self.down_pressed
    
    def set(self):
        return self.set_pressed

    def dst(self):
        return self.dst_pressed
