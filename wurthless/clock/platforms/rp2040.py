
from wurthless.clock.framework.platforms import registerPlatform

registerPlatform(u"rp2040",u"RP2040-based hardware", u"micropython")
registerPlatform(u"rpipico",u"Raspberry Pi Pico", u"rp2040")
registerPlatform(u"rpipicow",u"Raspberry Pi Pico W", u"rp2040")
