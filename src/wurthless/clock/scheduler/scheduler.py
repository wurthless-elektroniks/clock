#
# Event scheduler. asyncio / task APIs are not used.
# Written in an attempt to simplify logic flow in clockmain.
#
# This code is probably not 2038-proof.
# But then again, neither is the rest of this project.
#

import wurthless.clock.common.time64 as time

try:
    from typing import Callable
except:
    pass

class EventFiresAfter(object):
    def __init__(self, seconds):
        self._seconds = seconds

    def _calcNextFire(self, ts):
        return ts + self._seconds

class EventFiresEveryMinute(object):
    def __init__(self):
        pass

    def _calcNextFire(self, ts):
        return ts + (60 - (ts % 60))

class EventFiresImmediately(object):
    def _calcNextFire(self, ts):
        return ts

EVENT_FIRES_EVERY_MINUTE = EventFiresEveryMinute()
EVENT_FIRES_IMMEDIATELY  = EventFiresImmediately()

class Event(object):
    def __init__(self):
        self._callback = None

class Scheduler(object):
    def __init__(self):
        self._event_dict = {}
        self._event_queue = []

        self._last_time = int(time.time())
        self._scheduler_executing = False

    def tick(self):
        '''
        Run the scheduler main loop.
        '''
        ts = int(time.time())
        if self._last_time == ts:
            return
        self._last_time = ts
        self._runScheduler()

    def _runScheduler(self):
        if self._scheduler_executing:
            return
        
        self._scheduler_executing = True
        try:
            while len(self._event_queue) != 0:
                # peek first event in queue
                if self._last_time < self._event_queue[0]._fire_at:
                    return

                event = self._event_queue.pop(0)
                
                # careful: the event is free to modify the queue via APIs below
                event._callback()

                if event._repeat:
                    self._enqueueEvent(event)
        finally:
            self._scheduler_executing = False

    def createEvent(self, name: str, when: int, callback: Callable[[],None], repeat:bool=False):
        '''
        Registers a new event but does not start it.
        Call restartEvent() to start it.

        If repeat=True, event will be rescheduled upon expiry (default is False, which makes the event one-shot).
        '''

        if name in self._event_dict:
            raise RuntimeError("bug check: event '%s' registered twice" %(name))
        
        event = Event()
        event._name = name
        event._when = when
        event._callback = callback
        event._repeat = repeat

        self._event_dict[name] = event

    def _enqueueEvent(self, event: Event):
        # calc next fire
        ts = event._when._calcNextFire(int(time.time()))
        event._fire_at = ts

        queue_size = len(self._event_queue)

        insert_idx = 0

        if queue_size != 0:
            insert_idx = self._calcEventPos(ts, 0, queue_size-1)

        self._event_queue.insert(insert_idx, event)

    def _calcEventPos(self, when, left_finger, right_finger):
        if when < self._event_queue[left_finger]._fire_at:
            return left_finger
        elif self._event_queue[right_finger]._fire_at <= when:
            return right_finger + 1
        else:
            return self._calcEventPos(when, left_finger+1, right_finger-1)

    def cancelAllEvents(self):
        '''
        Deschedules all events without firing them.
        '''
        self._event_queue = []

    def cancelEvent(self, name: str):
        '''
        Deschedules an event but does not unregister it.
        '''
        idx = self._findEvent(name)
        if idx != -1:
            self._event_queue.pop(idx)

    def _findEvent(self, name: str):
        # lazy search by index
        for i in range(0, len(self._event_queue)):
            if self._event_queue[i]._name == name:
                return i
        return -1

    def isEventScheduled(self, name: str) -> bool:
        '''
        Return True if the given event is currently scheduled.
        '''
        return self._findEvent(name) != -1

    def fireEvent(self, name: str):
        '''
        Put the given event at the front of the queue and mark it to execute immediately.
        If the event is recurring, it will be rescheduled.
        If this is called outside of the normal scheduler loop, it will force the scheduler to run immediately.
        '''
        if name not in self._event_dict:
            raise RuntimeError("event not registered: %s" % (name))

        idx = self._findEvent(name)
        if idx != -1:
            event = self._event_queue.pop(idx)
        else:
            event = self._event_dict[name]
        
        event._fire_at = 0
        self._event_queue.insert(0, event) 
        self._runScheduler()

    def scheduleEvent(self, name: str):
        '''
        (Re)schedules an event to fire.
        '''
        if name not in self._event_dict:
            raise RuntimeError("event not registered: %s" % (name))

        idx = self._findEvent(name)
        if idx != -1:
            self._event_queue.pop(idx)

        self._enqueueEvent(self._event_dict[name])
