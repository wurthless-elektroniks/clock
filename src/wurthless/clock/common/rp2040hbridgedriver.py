'''
H-bridge driver for RP2040 or compatibles

An h-bridge driver is needed when driving VFD panels because the display won't be evenly lit otherwise
'''

from machine import Pin
import rp2
from rp2 import PIO

@rp2.asm_pio(set_init=[PIO.OUT_LOW]*2)
def hbridge_pio():
    wrap_target()
    set(pins, 1) [31]
    set(pins, 2) [31]
    wrap()

def hbridge_init(gpio_base: int):
    Pin(gpio_base, Pin.OUT)
    Pin(gpio_base+1, Pin.OUT)
    sm = rp2.StateMachine(7, hbridge_pio, freq=2400, set_base=Pin(gpio_base))
    sm.active(1)
