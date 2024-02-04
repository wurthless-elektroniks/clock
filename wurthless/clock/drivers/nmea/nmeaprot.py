#
# NMEA protocol parser/control.
#
# We do not implement location sensing, all that matters is the date/time and whether any satellites are up.
#

import re



def nmeaParseGsv(message):
    matches = re.match(u"^\\$[A-Z][A-Z]GSV,([0-9]),([0-9]),([0-9][0-9])",message)

    if matches is None:
        return None

    return [ int(matches.group(1)), int(matches.group(2)), int(matches.group(3)) ]

def nmeaParseZda(message):
    # 1 = hr
    # 2 = min
    # 3 = sec
    # 4 = day
    # 5 = hour
    # 6 = year
    matches = re.match(u"^\\$[A-Z][A-Z]ZDA,([0-9][0-9])([0-9][0-9])([0-9][0-9])\\.[0-9]+,([0-9][0-9]),([0-9][0-9]),([0-9][0-9][0-9][0-9]),([0-9][0-9]),([0-9][0-9])",message)
    if matches is None:
        return None

    # TODO: fix format
    return [ int(matches.group(1)),
             int(matches.group(2)),
             int(matches.group(3)),
             int(matches.group(4)),
             int(matches.group(5)),
             int(matches.group(6)),
             ]

# Parses the given bytemessage into a message.
# If mappers is not None, we assume we've passed in a dict of mappers
# pointing messageType->lambda where lambda = lambda msg : dostuff.
#
# Returns None if message invalid, "HANDLED" if message was passed off to a mapper,
# or the raw message if not handled.
def nmeaParseBytes(bytemessage, mappers=None):
    if bytemessage is None:
        return None

    if chr(bytemessage[0]) != '$':
        return None
    
    msg = bytemessage.decode('ascii')
    if mappers is not None:
        matches = re.match("^\\$([A-Z][A-Z][A-Z][A-Z][A-Z])", msg)
        if matches is not None:
            k = matches.group(1)
            if k in mappers:
                mappers[k](msg)
                return "HANDLED"

    return msg
