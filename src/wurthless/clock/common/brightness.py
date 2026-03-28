'''
Common brightness control logic
'''

# this should always be 1, so don't change it unless you want to break everything
BRIGHTNESS_MINIMUM_VALUE = 1

BRIGHTNESS_MAXIMUM_VALUE = 16

BRIGHTNESS_TOTAL_STEPS = (BRIGHTNESS_MAXIMUM_VALUE - BRIGHTNESS_MINIMUM_VALUE) + 1

def clamp_brightness(brightness: int) -> int:
    return max(BRIGHTNESS_MINIMUM_VALUE, min(brightness, BRIGHTNESS_MAXIMUM_VALUE))

def decrement_brightness(brightness: int) -> int:
    v = clamp_brightness(brightness) - 1
    return v if v >= BRIGHTNESS_MINIMUM_VALUE else BRIGHTNESS_MAXIMUM_VALUE

def increment_brightness(brightness: int) -> int:
    v = clamp_brightness(brightness) + 1
    return v if v <= BRIGHTNESS_MAXIMUM_VALUE else BRIGHTNESS_MINIMUM_VALUE
