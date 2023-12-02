from wurthless.clock.framework.platforms import platformBuilder
from wurthless.clock.drivers.nic.micropythonwifinic import MicropythonWifiNic
from wurthless.clock.common.ntp import NtpTimeSource

platformBuilder(u"rp2040",u"RP2040-based hardware", u"micropython") \
    .done()

platformBuilder(u"rpipico", u"Raspberry Pi Pico", u"rp2040") \
    .done()

platformBuilder(u"rpipicow", u"Raspberry Pi Pico W", u"rp2040") \
    .nicDriver( MicropythonWifiNic ) \
    .timesources( [ NtpTimeSource ] ) \
    .done()
