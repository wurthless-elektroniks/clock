# TMUCITW v8 - turn status LED on at boot time
from machine import Pin

Pin(26,Pin.OUT).value(1)
