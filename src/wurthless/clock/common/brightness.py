'''
Common brightness control logic
'''

from wurthless.clock.common.upy import make_const

# this should always be 1, so don't change it unless you want to break everything
BRIGHTNESS_MINIMUM_VALUE = make_const(1)

# Brightness control used to be in 8 steps, a holdover from the MAX7219 days.
# It is now 16 steps, which will break compatibility with setups like that.
# If you absolutely need 8-step brightness, change this to 8 and prepare to
# deal with a ton of broken code.
BRIGHTNESS_MAXIMUM_VALUE = make_const(16)

BRIGHTNESS_TOTAL_STEPS = make_const((BRIGHTNESS_MAXIMUM_VALUE - BRIGHTNESS_MINIMUM_VALUE) + 1)

def clamp_brightness(brightness: int) -> int:
    return max(BRIGHTNESS_MINIMUM_VALUE, min(brightness, BRIGHTNESS_MAXIMUM_VALUE))

def decrement_brightness(brightness: int) -> int:
    v = clamp_brightness(brightness) - 1
    return v if v >= BRIGHTNESS_MINIMUM_VALUE else BRIGHTNESS_MAXIMUM_VALUE

def increment_brightness(brightness: int) -> int:
    v = clamp_brightness(brightness) + 1
    return v if v <= BRIGHTNESS_MAXIMUM_VALUE else BRIGHTNESS_MINIMUM_VALUE
