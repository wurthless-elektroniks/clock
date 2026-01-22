#
# Globally-accessible config stuff.
# Anything that's registered here is assumed to be user-editable.
# Any cvar registered elsewhere is for pro users only.
# 

from wurthless.clock.cvars.cvars import registerCvar

registerCvar(u"config.display",
             u"brightness",
             u"Int",
             u"Brightness of display (value is from 1 to 8, default is 8).",
             8)

registerCvar(u"config.clock",
             u"utc_offset_seconds",
             u"Int",
             u"UTC offset in seconds. Default is 0 (plain ol' UTC).",
             0)

registerCvar(u"config.clock",
             u"dst_active",
             u"Boolean",
             u"DST active flag. Default is False (off).",
             False)

registerCvar(u"config.clock",
             u"dst_disable",
             u"Boolean",
             u"If true, disable DST entirely (needed in territories where there is no DST). Default is False (off).",
             False)

registerCvar("config.clock",
             "display_12hr_time",
             "Boolean",
             "Display 12 hour time in main loop. Default is False (prefer 24 hour time).",
             False)

registerCvar(u"config.nic",
             u"enable",
             u"Boolean",
             u"Enable network interface if present. Default is True.",
             True)

registerCvar(u"config.nic",
             u"wifi_ap_name",
             u"String",
             u"Name of Wifi access point (if connecting over Wi-Fi).",
             u"")

registerCvar(u"config.nic",
             u"wifi_ap_password",
             u"String",
             u"Wifi password (if connecting over Wi-Fi)",
             u"")
