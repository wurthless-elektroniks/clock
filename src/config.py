#
# Globally-accessible config stuff.
# Anything that's registered here is assumed to be user-editable.
# Any cvar registered elsewhere is for pro users only.
# 

from wurthless.clock.cvars.cvars import registerCvar

from wurthless.clock.common.brightness import BRIGHTNESS_MAXIMUM_VALUE

# Brightness of display.
registerCvar(u"config.display",
             u"brightness",
             u"Int",
             BRIGHTNESS_MAXIMUM_VALUE)

# UTC offset in seconds. Default is 0 (plain ol' UTC).
registerCvar(u"config.clock",
             u"utc_offset_seconds",
             u"Int",
             0)

# DST active flag. Default is False (off).
registerCvar(u"config.clock",
             u"dst_active",
             u"Boolean",
             False)

# If true, disable DST entirely (needed in territories where there is no DST). Default is False (off).
registerCvar(u"config.clock",
             u"dst_disable",
             u"Boolean",
             False)

# Display 12 hour time in main loop. Default is False (prefer 24 hour time).
registerCvar("config.clock",
             "display_12hr_time",
             "Boolean",
             False)

# Enable network interface if present. Default is True.
registerCvar(u"config.nic",
             u"enable",
             u"Boolean",
             True)

# Name of Wifi access point (if connecting over Wi-Fi).
registerCvar(u"config.nic",
             u"wifi_ap_name",
             u"String",
             u"")

# Wifi password (if connecting over Wi-Fi)
registerCvar(u"config.nic",
             u"wifi_ap_password",
             u"String",
             u"")
