#
# Input interface for Pico
#
from wurthless.clock.api.inputs import Inputs
from machine import Pin

GPIO_UP_PIN = 7
GPIO_DOWN_PIN = 8
GPIO_SET_PIN = 9
GPIO_DST_PIN = 11

class PicoInputs(Inputs):
    def __init__(self):
        print(u"""
PicoInputs initializing hardware.
Up = GP%d
Down = GP%d
Set = GP%d
        """ % (GPIO_UP_PIN, GPIO_DOWN_PIN, GPIO_SET_PIN))
        self.up_pin = Pin(GPIO_UP_PIN, Pin.IN, Pin.PULL_UP)
        self.down_pin = Pin(GPIO_DOWN_PIN, Pin.IN, Pin.PULL_UP)
        self.set_pin = Pin(GPIO_SET_PIN, Pin.IN, Pin.PULL_UP)
        self.dst_pin = Pin(GPIO_DST_PIN, Pin.IN, Pin.PULL_UP)

        self.up_pressed   = False
        self.down_pressed = False
        self.set_pressed  = False
        self.dst_pressed  = False
    
    def strobe(self):
        self.up_pressed   = self.up_pin.value() == 0
        self.down_pressed = self.down_pin.value() == 0
        self.set_pressed  = self.set_pin.value() == 0
        self.dst_pressed  = self.set_pin.value() == 0

    def up(self):
        return self.up_pressed
    
    def down(self):
        return self.down_pressed
    
    def set(self):
        return self.set_pressed

    def dst(self):
        return self.dst_pressed
