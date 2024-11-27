#
# NTP v4 support
#
# Reference: https://www.eecis.udel.edu/~mills/database/reports/ntp4/ntp4.pdf
#

def _ntpv4_transact(netcb):
    """
    Run NTPv4 transaction.

    netcb - callback. Takes query bytearray, sends it somewhere, returns response bytearray.
            Callback used here so we can abstract away sockets in testing.
    """

    # blank query, LI = 0, VN = 4, mode = 3 (client)
    query = bytearray(48)
    query[0] = 0b00011011

    response = netcb(query)

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
    # followed by extension fields.
    #
    # the NTP timestamps are NTPv3 backwards compatible
    # and contain no useful information as to what year it's supposed to be.
    # as such, time wraps back to the year 1900 when they overflow.



