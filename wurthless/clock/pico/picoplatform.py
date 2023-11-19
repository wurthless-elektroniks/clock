#
# Raspberry Pi Pico platform init stuff
#

from wurthless.clock.drivers.ds1307 import DS1307,ds1307Present
from machine import I2C




#
# picoPlatformInit(): Init platform
#
# Pico W will be detected automatically.
#
def picoPlatformInit(tot):

    print(u"picoPlatformInit(): setup in progress")

    # Check for time sources
    # On Pico W we will sync over Wifi if available


    pass