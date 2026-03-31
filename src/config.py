#
# Globally-accessible config stuff.
# Anything that's registered here is assumed to be user-editable.
# Any cvar registered elsewhere is for pro users only.
# 

from wurthless.clock.cvars.cvars import registerCvar

from wurthless.clock.common.brightness import BRIGHTNESS_MAXIMUM_VALUE

# Brightness of display.
registerCvar("config.display",
             "brightness",
             "Int",
             BRIGHTNESS_MAXIMUM_VALUE)

# UTC offset in seconds. Default is 0 (plain ol' UTC).
registerCvar("config.clock",
             "utc_offset_seconds",
             "Int",
             0)

# DST active flag. Default is False (off).
registerCvar("config.clock",
             "dst_active",
             "Boolean",
             False)

# If true, disable DST entirely (needed in territories where there is no DST). Default is False (off).
registerCvar("config.clock",
             "dst_disable",
             "Boolean",
             False)

# Display 12 hour time in main loop. Default is False (prefer 24 hour time).
registerCvar("config.clock",
             "display_12hr_time",
             "Boolean",
             False)

# Force manual mode; ignore all timesources.
registerCvar("config.clock",
             "force_manual",
             "Boolean",
             False)

# Enable network interface if present. Default is True.
registerCvar("config.nic",
             "enable",
             "Boolean",
             True)

# Name of Wifi access point (if connecting over Wi-Fi).
registerCvar("config.nic",
             "wifi_ap_name",
             "String",
             "")

# Wifi password (if connecting over Wi-Fi)
registerCvar("config.nic",
             "wifi_ap_password",
             "String",
             "")
