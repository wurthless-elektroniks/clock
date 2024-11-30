#
# NTP v4 support
#
# Reference: https://www.eecis.udel.edu/~mills/database/reports/ntp4/ntp4.pdf
#
# ntpv4 response format is:
#
# $00~$03: LI/VN/Mode/Stratum/Poll, probably not important
# $04~$07: root delay
# $08~$0B: root dispersion
# $0C~$0F: reference ID
# - this will contain the kiss code on error
#   and MUST be checked
# $10~$17: reference timestamp
# $18~$1F: origin timestamp
# $20~$27: receive timestamp
# $28~$2F: transmit timestamp
# followed by extension fields (none of which are currently useful)
#
# the NTP timestamps are NTPv3 backwards compatible
# and contain no useful information as to what year it's supposed to be.
# as such, time wraps back to the year 1900 when they overflow

import wurthless.clock.common.time64 as time64
from wurthless.clock.api.timesource import TIMESOURCE_MUST_FORGET, TIMESOURCE_RATE_LIMIT, TIMESOURCE_GENERIC_ERROR

try:
    import ustruct as struct
except:
    import struct

TMUCITW_NTP_EPOCH = 3849984000 # = 0xE57A1800, 2022 Jan 1st 00:00.00

def ntpv4_filter_error(refid) -> int:
    # Kiss o' Death fatal errors - DENY / RSTR
    if refid == "DENY" or refid == "RSTR":
        return TIMESOURCE_MUST_FORGET
    
    if refid == "RATE":
        return TIMESOURCE_RATE_LIMIT
    
    return TIMESOURCE_GENERIC_ERROR

def ntpv4_transact(netcb) -> int:
    """
    Run NTPv4 transaction.

    Returns 0 on failure, timestamp otherwise.
    This function WILL throw a RuntimeError if the server returns a fatal error.
    """
    # blank query, LI = 0, VN = 4, mode = 3 (client)
    query = bytearray(48)
    query[0] = 0b00100011
    response = netcb(query)

    # detect valid server response first (server MUST support v4)
    header = struct.unpack("!bbbb",response[0x00:0x04])
    if (header[0] & 0b00111000) != 0b00100000:
        print(u"NTPv4: unexpected response, wanted version 4 and server responded differently")
        return TIMESOURCE_GENERIC_ERROR
    
    # stratum field of 0 means error happened
    if header[1] == 0:
        refid = struct.unpack("!4s", response[0x0C:0x10])[0].decode("ascii")
        return ntpv4_filter_error(refid)
        
    timestamp = struct.unpack("!I", response[0x28:0x2C])[0]

    # catch timestamp underflow (all dates before 2022-01-01 00:00.00 UTC are considered "future")
    if timestamp < TMUCITW_NTP_EPOCH:
        timestamp += 0x0000000100000000
    
    epoch_year = time64.gmtime(0)[0]
    if epoch_year == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        delta = 3155673600
    elif epoch_year == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        delta = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(epoch_year))

    return timestamp - delta

