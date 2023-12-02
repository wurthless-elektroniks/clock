#
# Base Micropython platform
#

from wurthless.clock.framework.platforms import platformBuilder

from wurthless.clock.drivers.rtc.micropythonrtc import MicropythonRTC

platformBuilder(u"micropython", u"Base Micropython platform") \
    .rtcDriver( MicropythonRTC ) \
    .done()
