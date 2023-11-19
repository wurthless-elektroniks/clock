#
# Functions for converting UTC timestamps (single ints) to datetime tuples.
#
# The clock works exclusively on UTC for a good reason: it's because pretty much every timesource
# we can poll from will give us the time as a UTC timestamp.
#

import time

def timestampToTimeTuple(timestamp):
    return time.gmtime(timestamp)

def timeTupleToTimestamp(tuple):
    # piping the results of mktime directly to the caller can result in horrifically inaccurate timestamps,
    # because mktime assumes local timezone will be used.
    # we catch the delta in advance and return the correct timestamp that way.
    # wastes a bit of cpu time, but who cares.
    delta = time.mktime(time.localtime()) - time.mktime(time.gmtime())
    return int(time.mktime(tuple)) + delta
