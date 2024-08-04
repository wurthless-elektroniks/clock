#
# Code formerly in esp32maskdisplay.py.
# Not sure where to move it.
#

import sys
from machine import mem32

def configureEsp32C3IoPins():
    if sys.implementation._machine.find("ESP32C3") >= 0:
        GPIO_OUT_REG = 0x60004004

        # micropython sucks and will not let us grab pins 18 or 19 as I/Os
        # although, hilariously, it allows us to try grabbing pins 11-17.
        print(u"******* ESP32-C3 detected. hacking around micropython limitations *******")
        print(u"killing USB-JTAG. if i don't see you on the other side, adios!")

        # disable USB PHY
        mem32[0x60043018] = 0x00000000

        print(u"grabbing pins 18/19 and setting them up as outputs")

        # set pins 18/19 as outputs
        mem32[0x60004024] |= (1 << 18) | (1 << 19)

        # configure pins 18/19 on I/O mux to match how the others are configured.
        # unfortunately, it seems pins 18/19 are limited in how much current they
        # can deliver so those segments might be dimmer than the others.
        # more testing to be done later.
        #
        #                     fedcba9876543210
        mem32[0x6000904C] = 0b0000111101101011
        mem32[0x60009050] = 0b0000111101101011

        print(u"esp32c3 platform configured. have a nice day!")