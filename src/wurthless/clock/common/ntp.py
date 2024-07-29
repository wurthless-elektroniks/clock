#
# NTP-based timesource
#
# This is a conversion of micropython's ntptime to work within this framework.
#

import time
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

from wurthless.clock.api.timesource import TimeSource
from wurthless.clock.cvars.cvars import registerCvar

# cvars
registerCvar(u"wurthless.clock.common.ntp", u"host",    u"String", u"NTP server to use when fetching time.", u"pool.ntp.org")
registerCvar(u"wurthless.clock.common.ntp", u"timeout", u"Int",    u"NTP socket timeout.", 1)

class NtpTimeSource(TimeSource):
    def __init__(self, tot):
        self.tot = tot

    def getUtcTime(self):
        if self.tot.nic().isUp() is False:
            return 0

        try:
            query = bytearray(48)
            query[0] = 0x1B
            addr = socket.getaddrinfo(self.tot.cvars().get(u"wurthless.clock.common.ntp",u"host"), 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.settimeout(self.tot.cvars().get(u"wurthless.clock.common.ntp",u"timeout"))
                res = s.sendto(query, addr)
                msg = s.recv(48)
            finally:
                s.close()
            val = struct.unpack("!I", msg[40:44])[0]

            epochYear = time.gmtime(0)[0]
            if epochYear == 2000:
                # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
                delta = 3155673600
            elif epochYear == 1970:
                # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
                delta = 2208988800
            else:
                raise Exception("Unsupported epoch: {}".format(epochYear))

            return val - delta

        except Exception as e:
            print(u"NtpTimeSource: unable to grab time over NTP")
            return 0
