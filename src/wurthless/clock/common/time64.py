#
# Workaround for micropython's faulty time implementation (vulnerable to the 2038 bug).
# TMUCITW timezone setting is assumed to always be UTC.
#
# The bug:
# When the RTC timestamp is 0x80000000 or greater, bad things happen.
# This occurs at the Unix epoch of 2038/01/19 03:14.07
# and at the Micropython epoch of 2068/01/19 03:14.07.
# (Epoch varies depending on what python runtime we're using.)
#
# This bug affects:
# - time.gmtime(timestamp) - immediate typeerror exception
# - time.localtime(timestamp) - immediate typeerror exception
# - time.time() - returns negative integer
#
# Functions seemingly unaffected:
# - time.mktime(struct_time): returns expected unsigned int
#

import time

# const for converting 2038/01/19 03:14.07 -> 1978/01/19 03:14.07.
# 1978 works here because 1976 and 2036 are both leap years,
# as are 1980 and 2040.
#
# in micropython land, the epoch is typically 2000/01/01
# with the overflow happening at 2068/01/19 03:14.07.
# either way works here.
_2038_TO_1978_ERA_OFFSET = 0x70DBD880 # = 1893456000 = (0x80000000 - 254027648)

# ------------------------------------------------------------------------------------------

def _filter_overflow(seconds : float, callback) -> time.struct_time:
    '''
    Applies 2038 bug workaround to the operation in question.
    callback MUST accept a timestamp in seconds.
    '''
    ts = int(seconds)
    if ts >= 0x80000000:
        ts -= _2038_TO_1978_ERA_OFFSET
        faketime = callback(ts)
        return ( faketime[0] + 60, faketime[1], faketime[2], faketime[3], faketime[4], faketime[5], faketime[6], faketime[7] )
    else:
        return callback(ts)

def gmtime(seconds : float | None = None) -> time.struct_time:
    if seconds is not None:
        return time.gmtime()
    else:
        return _filter_overflow(seconds, lambda t: time.gmtime(t))

def localtime(seconds : float | None = None) -> time.struct_time:
    if seconds is not None:
        return time.localtime()
    else:
        return _filter_overflow(seconds, lambda t: time.localtime(t))

def time():
    # TODO: real time module returns negative values upon overflow
    return time.time()

def mktime(tuple):
    return time.mktime(tuple)

def sleep(seconds):
    return time.sleep(seconds)
