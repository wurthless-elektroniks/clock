#
# Platform definitions for The Most Useless Clock in the World hardware and its various deployments
#

from wurthless.clock.framework.platforms import registerPlatform

registerPlatform(u"tmucitw_rp2040_old",u"TMUCITW, RPi Pico W-based, versions 2-4", u"rpipicow")
registerPlatform(u"tmucitw_rp2040_new",u"TMUCITW, RPi Pico W-based, version 5", u"rpipicow")

