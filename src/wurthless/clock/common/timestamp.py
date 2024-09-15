#
# Functions for converting UTC timestamps (single ints) to datetime tuples.
#
# The clock works exclusively on UTC for a good reason: it's because pretty much every timesource
# we can poll from will give us the time as a UTC timestamp.
#

import time

def getTimestampForNextMinute(timestamp):
    firsttuple = timestampToTimeTuple(timestamp)

    ts = timestamp
    # this is very slow, but is used to catch leap seconds
    # (of course, that assumes our runtime knows about those)
    while True:
        ts += 1
        nexttuple = timestampToTimeTuple(ts)
        if firsttuple[4] != nexttuple[4]:
            break    
    return ts


def timestampToTimeTuple(timestamp):
    return time.gmtime(timestamp)

def timeTupleToTimestamp(tuple):
    # piping the results of mktime directly to the caller can result in horrifically inaccurate timestamps,
    # because mktime assumes local timezone will be used.
    # we catch the delta in advance and return the correct timestamp that way.
    # wastes a bit of cpu time, but who cares.
    delta = time.mktime(time.localtime()) - time.mktime(time.gmtime())
    return int(time.mktime(tuple)) + delta

# util function commonly used to render the current hour
# return array [hour, is_pm]. if running in 24 hour mode, simply return [ hour, False ].
# didn't know where to put this, it will live in here for now...
def autoformatHourIn12HourTime(tot, hour):
    # TODO: 12-hour time will return someday, but not here
    return [ hour, False ]