
#
# Main clock functions
# This is mostly based on the code flow in the old clock.ino, but a bit cleaner.
#

import sys
import time

try:
    from utime import sleep_ms
except:
    sleep_ms = lambda a : time.sleep(a / 1000)

from wurthless.clock.api.display import COLON_STATE_BLINK, COLON_STATE_OFF, COLON_STATE_ON
from wurthless.clock.api.tot import ToT
from wurthless.clock.burnin import burnin,inputTest
from wurthless.clock.common.messages import messagesDisplaySync,messagesDisplayErr,messagesDisplayOops,messagesDisplayCfg
from wurthless.clock.common.timestamp import timestampToTimeTuple,timeTupleToTimestamp,autoformatHourIn12HourTime,getTimestampForNextMinute
from wurthless.clock.webserver.webserver import serverMain
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.input.debouncedinputs import DebouncedInputs
from wurthless.clock.drivers.input.delayedinputs import DelayedInputs
from wurthless.clock.common.prompt import promptYear, promptMonthOrDay, promptTime, promptDst
from wurthless.clock.common.bcd import unpackBcd
from wurthless.clock.scheduler.scheduler import Scheduler, EVENT_FIRES_EVERY_MINUTE, EVENT_FIRES_IMMEDIATELY, EventFiresAfter

################################################################################################################
#
# Cvars (specific to the logic in this file)
#
################################################################################################################

registerCvar(u"wurthless.clock.clockmain",
             u"set_and_dst_no_debounce",
             u"Boolean",
             u"If True, pressing SET and DST execute their actions immediately (needed when running in curses). Default behavior is False (user must hold buttons to execute those actions).",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"disable_calendar",
             u"Boolean",
             u"If True, disable calendar, and assume all date settings will be 2023-01-01. Default is False (calendar is enabled).",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"digit_0_truncated",
             u"Boolean",
             u"If True, digit 0 only has segments B and C populated, with segmetn A indicating p.m. Default is False.",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"autosync_frequency",
             u"Int",
             u"Interval time in seconds between clock synchronization. Default is 7200 (every 2 hours). Used only if timesources are present.",
             7200)

registerCvar(u"wurthless.clock.clockmain",
             u"settings_write_delay",
             u"Int",
             u"Interval time in seconds to delay saving settings. Default is 1800 (30 minutes). Needed to prevent wearing down the system flash.",
             1800)

registerCvar(u"wurthless.clock.clockmain",
             u"force_server",
             u"Boolean",
             u"If True, force server mode (needed for testing).",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"force_burnin",
             u"Boolean",
             u"If True, force burn-in mode (needed for testing).",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"tickrate",
             u"Int",
             u"Framerate in Hz. Default is 25.",
             25)

registerCvar("wurthless.clock.clockmain",
             "nixieroto",
             "Boolean",
             "If True, rotate all digits at the minute mark (avoids Nixie cathode poisoning). Default is False.",
             False)

def configMode(tot: ToT):
    utc_offset = tot.cvars().get(u"config.clock",u"utc_offset_seconds")
    dst_active = tot.cvars().get("config.clock", "dst_active")

    tot.display().setColonState(COLON_STATE_OFF)

    # brightness always 8 coming into this loop
    tot.display().setBrightness(8)

    # wrap inputs (simplifies keeping track of pushbutton states between prompts)
    direct_inputs = tot.inputs()
    inputs = DebouncedInputs(direct_inputs)
    inputs.strobe()

    # if RTC already configured, grab current time
    if tot.rtc().isUp():
        timetuple = timestampToTimeTuple( tot.rtc().getUtcTime() + utc_offset + (3600 if dst_active else 0))
        year  = timetuple[0]
        month = timetuple[1]
        day   = timetuple[2]
        hour  = timetuple[3]
        minute = timetuple[4]
    else:
        year = 2022
        month = 1
        day = 1
        hour = 0
        minute = 0

    # prompt, in order: year, month, date, hour, minute
    # If the calendar function is disabled, just prompt for hour and minute

    if tot.cvars().get(u"wurthless.clock.clockmain",u"disable_calendar") is False:
        year = promptYear(tot, inputs, year)
        month = promptMonthOrDay(tot, inputs, month, 12)
        maxdays = 30
        if month in [1,3,5,7,8,10,12]:
            maxdays = 31
        elif month == 2:
            maxdays = 29 if (year % 4) == 0 else 28

        day = promptMonthOrDay(tot, inputs, day, maxdays)

    tot.display().setColonState(COLON_STATE_ON)
    updated_time = promptTime(tot, inputs, hour, minute)
    hour    = updated_time[0]
    minute  = updated_time[1]

    # last input to prompt for is DST (if not inhibited by software)
    tot.display().setColonState(COLON_STATE_OFF)
    dst_active = False

    if inputs.is_dst_dipswitch():
        direct_inputs.strobe()
        dst_active = direct_inputs.dst()
    elif tot.cvars().get("config.clock", "dst_disable") is False:
        dst_active = promptDst(tot, inputs, dst_active)

    tot.cvars().set("config.clock", "dst_active", dst_active)
    tot.cvars().save()

    # pack results and set RTC
    packed_time = ( year, month, day, hour, minute, 0, 0, 0, 0 )
    tot.rtc().setUtcTime( (timeTupleToTimestamp(packed_time) - utc_offset ) - ( 3600 if dst_active is True else 0 ) )
    
    # restore brightness before returning to caller, as there's no guarantee the caller will do that for us
    tot.display().setBrightness(tot.cvars().get(u"config.display",u"brightness"))

#
# Draw/update the display
#
def renderDisplay(tot: ToT, mode: int):
    # get UTC time straight from the RTC (VERY SLOW)
    utctime = tot.rtc().getUtcTime()

    utc_offset = tot.cvars().get(u"config.clock",u"utc_offset_seconds")
    dst_active = tot.cvars().get(u"config.clock",u"dst_active")

    utctime += utc_offset
    if dst_active is True:
        utctime += 3600

    tuple = timestampToTimeTuple(utctime)
    if mode == 0:
        hour    = tuple[3]
        minute  = tuple[4]
        bcd = unpackBcd(hour, minute)
        tot.display().setDigitsNumeric( bcd[0], bcd[1], bcd[2], bcd[3] )
        tot.display().setColonState(COLON_STATE_BLINK)
    elif mode == 1:
        year = tuple[0]
        bcd = unpackBcd(year / 100, year % 100)
        # 12-hour assumes that many of the segments on digit 0 will not be populated,
        # so in 12-hour mode, only display the last two digits of the year.
        # these things won't be working in 100 years time, because we'll all be dead by then
        tot.display().setDigitsNumeric( bcd[0], bcd[1], bcd[2], bcd[3] )
        tot.display().setColonState(COLON_STATE_OFF)
    elif mode == 2:
        month = tuple[1]
        bcd = unpackBcd(0, month)
        tot.display().setDigitsNumeric( None, None, bcd[2], bcd[3] )
        tot.display().setColonState(COLON_STATE_OFF)
    elif mode == 3:
        day = tuple[2]
        bcd = unpackBcd(0, day)
        tot.display().setDigitsNumeric( None, None, bcd[2], bcd[3] )
        tot.display().setColonState(COLON_STATE_OFF)

def syncTime(tot: ToT, suppressError:bool=False) -> bool:
    '''
    Return True if the clock was successfully able to synchronize to a timezone.
    Return False otherwise.
    '''
    # display "SYNC"
    messagesDisplaySync(tot.display())
    
    # enumerate over all time sources until something answers
    t = 0
    for timesource in tot.timesources():
        t = timesource.getUtcTime()
        if t > 0: break
    
    # TODO: this does NOT handle rate limit/"forget us" error codes yet.
    if t > 0:
        tot.rtc().setUtcTime(t)
        return True
    elif tot.rtc().isUp() is True and suppressError is True:
        # skip "Err" message if RTC is already configured
        return False
    else:
        # otherwise, display "Err"
        messagesDisplayErr(tot.display())

        # wait for user to press button
        while True:
            tot.inputs().strobe()
            if tot.inputs().set() is True:
                break

        tot.display().blank()
        
        # wait for user to release button
        while True:
            tot.inputs().strobe()
            if tot.inputs().set() is False:
                break

        return False

################################################################################################################
#
# init()
#
################################################################################################################

def init(tot: ToT):
    # At the very least, we need the display installed,
    # else panic and exit immediately
    if tot.display() is None:
        print(u"Display driver not installed, no point continuing execution.")
        return
    
    # If no RTC, panic
    if tot.rtc() is None:
        print(u"No RTC installed, no point continuing execution.")
        return
    
    # if NIC present, bring it up
    if tot.cvars().get(u"config.nic", u"enable") is True and tot.nic() is not None and tot.nic().isUp() is False:
        tot.nic().initAsClient()
    
    if tot.rtc().readOnly() is False:
        # Synchronize time to timesource, if one is available.
        if tot.timesources() is not None and tot.timesources() != []:
            syncTime(tot)

        # If RTC is not setup by this point, prompt for time.
        if tot.rtc().isUp() is False:
            configMode(tot)

    elif tot.rtc().isUp() is False:
        print(u"Read-only RTC is not started. Make your code less shitty please.")
        return

################################################################################################################
#
# loop()
#
################################################################################################################

def loop(tot: ToT):
    brightness = tot.cvars().get(u"config.display",u"brightness")
    if not (1 <= brightness and brightness <= 8):
        brightness = 8
    tot.display().setBrightness(brightness) 

    dst_is_dipswitch = tot.inputs().is_dst_dipswitch()
    set_and_dst_no_debounce = tot.cvars().get(u"wurthless.clock.clockmain", u"set_and_dst_no_debounce")
    disable_calendar = tot.cvars().get(u"wurthless.clock.clockmain", u"disable_calendar")

    rtc_read_only = tot.rtc().readOnly() 
    dst_disable = tot.cvars().get(u"config.clock",u"dst_disable") 

    cfg_writeback_delay = tot.cvars().get(u"wurthless.clock.clockmain",u"settings_write_delay")

    nixieroto = tot.cvars().get(u"wurthless.clock.clockmain",u"nixieroto")

    global displaymode
    displaymode = 0
    timesource_present = tot.timesources() is not None and tot.timesources() != []
    
    inputs = tot.inputs()

    tickrate = tot.cvars().get(u"wurthless.clock.clockmain",u"tickrate")
    tick_time_ms = int((1.0 / tickrate)*1000.0)
    ticks_per_second = int(1000.0 / tick_time_ms)
    dst_set_hold_delay_tick_count = ticks_per_second * 5

    direct_inputs = inputs
    if set_and_dst_no_debounce is False:
        delayedinputs = DelayedInputs(inputs)
        delayedinputs.up_delay(0)
        delayedinputs.down_delay(0)
        delayedinputs.set_delay(dst_set_hold_delay_tick_count)
        delayedinputs.dst_delay(dst_set_hold_delay_tick_count)
        inputs = DebouncedInputs(delayedinputs)

    def _rerenderDisplay():
        if nixieroto and displaymode == 0 and (tot.rtc().getUtcTime() % 60) < 3:
            for i in range(0,10):
                tot.display().setDigitsNumeric(i,i,i,i)
                sleep_ms(200)

        renderDisplay(tot, displaymode)

    scheduler = Scheduler()

    scheduler.createEvent("writebackCfg",
                          EventFiresAfter(cfg_writeback_delay),
                          lambda: tot.cvars().save())

    scheduler.createEvent("rerenderDisplay",
                          EVENT_FIRES_EVERY_MINUTE,
                          _rerenderDisplay,
                          repeat=True)
                          
    def autosyncAttempt():
        syncTime(tot, suppressError=True)
        resetState()

    scheduler.createEvent("autosync",
                            EventFiresAfter(tot.cvars().get(u"wurthless.clock.clockmain",u"autosync_frequency")),
                            lambda: autosyncAttempt(),
                            repeat=True)

    def autoreturnToDisplayMode0():
        # awful hack, but otherwise this code doesn't work
        global displaymode
        displaymode = 0

        scheduler.fireEvent("rerenderDisplay")

    scheduler.createEvent("autoreturnToDisplayMode0",
                          EventFiresAfter(3),
                          lambda: autoreturnToDisplayMode0())

    # function will be called several times
    def resetState():
        cfg_save_pending = scheduler.isEventScheduled("writebackCfg")
        displaymode_change_pending = scheduler.isEventScheduled("autoreturnToDisplayMode0")

        scheduler.cancelAllEvents()
        inputs.reset()

        if cfg_save_pending is True:
            scheduler.scheduleEvent("writebackCfg")

        if timesource_present is True:
            scheduler.scheduleEvent("autosync")

        if displaymode_change_pending is True:
            scheduler.fireEvent("autoreturnToDisplayMode0")
        else:
            scheduler.fireEvent("rerenderDisplay")

    resetState()

    while True:
        scheduler.tick()
        if inputs.strobe() is False:
            if dst_is_dipswitch:
                current_dst_setting = tot.cvars().get("config.clock", "dst_active")
                new_dst_setting = direct_inputs.dst()
                if new_dst_setting != current_dst_setting:
                    tot.cvars().set("config.clock", "dst_active",new_dst_setting)
                    scheduler.fireEvent("rerenderDisplay")

            sleep_ms(tick_time_ms)
            continue

        # Pressing UP changes brightness in descending order.
        # If brightness is at minimum, reset to highest brightness.
        if inputs.up():
            brightness -= 1
            if not (1 <= brightness and brightness <= 8):
                brightness = 8
            tot.display().setBrightness(brightness) 
            tot.cvars().set(u"config.display",u"brightness",brightness)
            scheduler.scheduleEvent("writebackCfg")

        # Pressing DOWN will toggle between displaymodes
        # in this order: year, month, day, time
        # If the displaymode goes off of time for a while, switch back to time.
        # DOWN does nothing if calendar mode disabled.
        elif disable_calendar is False and inputs.down() is True:
            displaymode += 1
            displaymode &= 3
            scheduler.fireEvent("rerenderDisplay")
            if displaymode != 0:
                scheduler.scheduleEvent("autoreturnToDisplayMode0")
            else:
                scheduler.cancelEvent("autoreturnToDisplayMode0")

        # Pressing and holding SET for long enough will go to configuration mode
        # if we are allowed to configure the RTC at all.
        # If any timesources are present, attempt synchronization before running config mode.
        elif rtc_read_only is False and inputs.set() is True:
            if (timesource_present is False or syncTime(tot, suppressError=False) is False):
                configMode(tot)

            # previously scheduled events are assigned to times that are no longer valid,
            # and debounce logic needs to be reset anyway
            resetState()
  
        elif dst_is_dipswitch is False and dst_disable is False and inputs.dst() is True:
            dst = tot.cvars().get(u"config.clock",u"dst_active")
            dst = not dst
            tot.cvars().set(u"config.clock",u"dst_active",dst)
            scheduler.scheduleEvent("writebackCfg")
            scheduler.fireEvent("rerenderDisplay")

        # ---- end handle inputs ----
        sleep_ms(tick_time_ms)

def clockMain(tot: ToT):
    tot.inputs().strobe()

    if tot.inputs().is_dst_dipswitch() is False and tot.inputs().dst():
        inputTest(tot)

    # if DOWN held on reset, go to burnin / demo mode
    force_burnin = tot.cvars().get(u"wurthless.clock.clockmain", u"force_burnin")
    if force_burnin or tot.inputs().down():
        burnin(tot)
    
    if tot.cvars().get(u"config.nic", u"enable") is True and tot.nic() is not None:
        # enter webserver config mode when SET is held on reset
        force_server = tot.cvars().get(u"wurthless.clock.clockmain", u"force_server")
        if tot.inputs().set() or force_server:
            # display "cfg"
            tot.display().setBrightness(8)
            messagesDisplayCfg(tot.display())

            serverMain(tot)

    # the ghost of Arduino past refuses to go away
    init(tot)
    while True:
        try:
            loop(tot)
        except Exception as e:
            # display "ooPS"
            messagesDisplayOops(tot.display())
            raise e
