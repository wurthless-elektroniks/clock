
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.api.timesource import TimeSource, TIMESOURCE_GENERIC_ERROR
from wurthless.clock.common.ntp4prot import ntpv4_transact

try:
    import usocket as socket
except:
    import socket

registerCvar(u"wurthless.clock.common.ntp4", u"host",    u"String", u"NTP server to use when fetching time.", u"pool.ntp.org")
registerCvar(u"wurthless.clock.common.ntp4", u"timeout", u"Int",    u"NTP socket timeout.", 1)

class Ntp4TimeSource(TimeSource):
    def __init__(self, tot):
        self.tot = tot

    def getUtcTime(self):
        if self.tot.nic().isUp() is False:
            return TIMESOURCE_GENERIC_ERROR

        try:
            addr = socket.getaddrinfo(self.tot.cvars().get(u"wurthless.clock.common.ntp4",u"host"), 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            def _transact(query):
                s.settimeout(self.tot.cvars().get(u"wurthless.clock.common.ntp4",u"timeout"))
                res = s.sendto(query, addr)
                return s.recv(48)
            
            try:
                return ntpv4_transact(lambda q: _transact(q))
            finally:
                s.close()
        except Exception as e:
            print(u"Ntp4TimeSource: unable to grab time over NTP")
            return TIMESOURCE_GENERIC_ERROR
