
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

from wurthless.clock.burnin import burnin
from wurthless.clock.common.timestamp import timestampToTimeTuple,timeTupleToTimestamp
from wurthless.clock.common.sevensegment import sevensegNumbersToDigits
from wurthless.clock.webserver.webserver import serverMain
from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.drivers.input.debouncedinputs import DebouncedInputs

TICK_TIME_MS = 10
snooze = lambda : sleep_ms(TICK_TIME_MS)

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
             u"use_12hr",
             u"Boolean",
             u"If True, this is a 12-hour clock (only 2 segments on digit 0, with segment A indicating p.m.). Default is False (all segments on digit 0 populated).",
             False)

registerCvar(u"wurthless.clock.clockmain",
             u"sync_frequency",
             u"Int",
             u"Interval time in seconds between clock synchronization. Default is 86400 (24 hours). Used only if timesources are present.",
             86400)

registerCvar(u"wurthless.clock.clockmain",
             u"settings_write_delay",
             u"Int",
             u"Interval time in seconds to delay saving settings. Default is 36000 (10 hours). Needed to prevent wearing down the system flash.",
             36000)

registerCvar(u"wurthless.clock.clockmain",
             u"force_server",
             u"Boolean",
             u"If True, force server mode (needed for testing).",
             False)


# util function commonly used to render the current hour
# return array [hour, is_pm]. if running in 24 hour mode, simply return [ hour, False ].
def autoformatHourIn12HourTime(tot, hour):
    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr") is True
    if use_12hr:
        is_pm = False
        if hour > 12:
            hour -= 12
            is_pm = True
        elif hour == 0:
            hour = 12
        return [ hour, is_pm ]
    else:
        return [ hour, False ]


################################################################################################################
#
# Config mode
#
################################################################################################################

def promptYear(tot, inputs, year):
    # 12 hour clocks do not have enough digits to display the full year
    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr") is True

    # if value is already out of range, clamp it
    if year < 2022:
        year = 2022
    elif year > 2099:
        year = 2099

    year_inp = year
    flash_state = False
    while True:
        bcd = unpackBcd(year_inp / 100, year_inp % 100)
        digs = sevensegNumbersToDigits( None if use_12hr is True else bcd[0], None if use_12hr is True else bcd[1], bcd[2], bcd[3] )
        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        tot.display().setBrightness( 8 if flash_state else 2 )

        inputs.strobe()

        if inputs.up():
            year_inp += 1
            year_inp = 2022 if year_inp > 2099 else year_inp
            flash_state = False
        elif inputs.down():
            year_inp -= 1
            year_inp = 2099 if year_inp < 2022 else year_inp
            flash_state = False
        elif inputs.set():
            return year_inp
        else:
            flash_state = not flash_state
            snooze()

def promptMonthOrDay(tot, inputs, valin, maxval):
    flash_state = False
    inp = valin

    # if value is already out of range, clamp it
    if valin > maxval:
        valin = maxval

    while True:
        bcd = unpackBcd(0, inp)
        digs = sevensegNumbersToDigits( None, None, bcd[2], bcd[3]  )
        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        tot.display().setBrightness( 8 if flash_state else 2 )

        inputs.strobe()
        if inputs.up():
            inp += 1
            inp = 1 if inp > maxval else inp
            flash_state = False
        elif inputs.down():
            inp -= 1
            inp = maxval if inp == 0 else inp
            flash_state = False
        elif inputs.set():
            return inp
        else:
            flash_state = not flash_state
            snooze()

def promptTime(tot, inputs, hour, minute):
    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr") is True
    flash_state = False

    retval = [ 0, 0 ]

    inp = hour

    while True:
        hour_visible = autoformatHourIn12HourTime(tot, inp)
        bcd = unpackBcd(inp, 0)
        digs = sevensegNumbersToDigits( bcd[0], bcd[1], None, None )

        # set segment A to indicate pm in 12-hour mode
        if use_12hr and hour_visible[1] is True:
            digs[0] |= 1

        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        tot.display().setBrightness( 8 if flash_state else 2 )

        inputs.strobe()
        if inputs.up():
            inp = 0 if inp == 23 else inp + 1
            flash_state = False
        elif inputs.down():
            inp = 23 if inp == 0 else inp - 1
            flash_state = False
        elif inputs.set():
            retval[0] = inp
            break
        else:
            flash_state = not flash_state
            snooze()

    flash_state = False
    inp = minute
    while True:
        hour_visible = autoformatHourIn12HourTime(tot, retval[0])
        bcd = unpackBcd(retval[0], inp)
        digs = sevensegNumbersToDigits( bcd[0], bcd[1], bcd[2], bcd[3] )

        # set segment A to indicate pm in 12-hour mode
        if use_12hr and hour_visible[1] is True:
            digs[0] |= 1

        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        tot.display().setBrightness( 8 if flash_state else 2 )

        inputs.strobe()
        if inputs.up():
            inp = 0 if inp == 59 else inp + 1
            flash_state = False
        elif inputs.down():
            inp = 59 if inp == 0 else inp - 1
            flash_state = False
        elif inputs.set():
            retval[1] = inp
            return retval
        else:
            flash_state = not flash_state
            snooze()

def promptDst(tot,inputs,dst):
    flash_state = False
    inp = dst
    while True:
        if flash_state is False:
            # "dST"
            tot.display().setDigitsBinary(0b00000000, 0b01011110, 0b01101101, 0b01111000)
        else: 
            # either "oFF" or "on"
            if inp is True:
                tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01010100, 0b00000000)
            else:
                tot.display().setDigitsBinary(0b00000000, 0b1011100, 0b01110001, 0b01110001)

        inputs.strobe()
        if inputs.up() or inputs.down():
            inp = not inp
            flash_state = False
        elif inputs.set():
            return inp
        else:
            flash_state = not flash_state
        snooze()


def configMode(tot):
    utc_offset = tot.cvars().get(u"config.clock",u"utc_offset_seconds")

    # brightness always 8 coming into this loop
    tot.display().setBrightness(8)

    # wrap inputs (simplifies keeping track of pushbutton states between prompts)
    inputs = DebouncedInputs(tot.inputs())
    inputs.strobe()


    # if RTC already configured, grab current time
    if tot.rtc().isUp():
        timetuple = timestampToTimeTuple( tot.rtc().getUtcTime() + utc_offset )        
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

    updated_time = promptTime(tot, inputs, hour, minute)
    hour    = updated_time[0]
    minute  = updated_time[1]

    # last input to prompt for is DST (if not inhibited by software)
    dst_active = False
    if tot.cvars().get(u"config.clock",u"dst_disable") is False:
        dst_active = tot.cvars().get(u"config.clock",u"dst_active")
        dst_active = promptDst(tot, inputs, dst_active)
        tot.cvars().set(u"config.clock",u"dst_active",dst_active)
        tot.cvars().save()

    # pack results and set RTC
    packed_time = ( year, month, day, hour, minute, 0, 0, 0, 0 )
    tot.rtc().setUtcTime( (timeTupleToTimestamp(packed_time) - utc_offset ) - ( 3600 if dst_active is True else 0 ) )
    
    # restore brightness before returning to caller, as there's no guarantee the caller will do that for us
    tot.display().setBrightness(tot.cvars().get(u"config.display",u"brightness"))

def unpackBcd(a,b):
    buf = [ 0,0,0,0 ]
    buf[1] = int(a % 10)
    buf[0] = int((a - buf[1]) / 10)
    buf[3] = int(b % 10)
    buf[2] = int((b - buf[3]) / 10)
    return buf

#
# Draw/update the display
#
def renderDisplay(tot, mode):
    utctime = tot.rtc().getUtcTime()

    utc_offset = tot.cvars().get(u"config.clock",u"utc_offset_seconds")
    dst_active = tot.cvars().get(u"config.clock",u"dst_active")
    use_12hr = tot.cvars().get(u"wurthless.clock.clockmain",u"use_12hr")

    utctime += utc_offset
    if dst_active is True:
        utctime += 3600

    tuple = timestampToTimeTuple(utctime)
    if mode == 0:
        hour    = tuple[3]
        minute  = tuple[4]
        if use_12hr is True:
            h = autoformatHourIn12HourTime(tot, hour)
            bcd = unpackBcd(h[0], minute)
            digs = sevensegNumbersToDigits( None if h[0] < 10 else bcd[0], bcd[1], bcd[2], bcd[3] )
            if h[1] is True:
                bcd[0] |= 1 # in 12-hour mode, segment A on digit 0 is used to indicate AM/PM
            tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
        else:
            bcd = unpackBcd(hour, minute)
            digs = sevensegNumbersToDigits( bcd[0], bcd[1], bcd[2], bcd[3] )
            tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
    elif mode == 1:
        year = tuple[0]
        bcd = unpackBcd(year / 100, year % 100)
        # 12-hour assumes that many of the segments on digit 0 will not be populated,
        # so in 12-hour mode, only display the last two digits of the year.
        # these things won't be working in 100 years time, because we'll all be dead by then
        digs = sevensegNumbersToDigits( None if use_12hr is True else bcd[0], None if use_12hr is True else bcd[1], bcd[2], bcd[3] )
        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
    elif mode == 2:
        month = tuple[1]
        bcd = unpackBcd(0, month)
        digs = sevensegNumbersToDigits( None, None, bcd[2], bcd[3] )
        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
    elif mode == 3:
        day = tuple[2]
        bcd = unpackBcd(0, day)
        digs = sevensegNumbersToDigits( None, None, bcd[2], bcd[3] )
        tot.display().setDigitsBinary( digs[0], digs[1], digs[2], digs[3] )
    
    
#
# syncTime()
#
# Return True if the clock was successfully able to synchronize to a timezone.
# Return False otherwise.
#
def syncTime(tot, suppressError = False):
    # display "SYNC"
    tot.display().setDigitsBinary(0b01101101, 0b01101110, 0b00110111, 0b00111001)

    # enumerate over all time sources until something answers
    t = 0
    for timesource in tot.timesources():
        t = timesource.getUtcTime()
        if t != 0: break
    
    if t != 0:
        tot.rtc().setUtcTime(t)
        return True
    elif tot.rtc().isUp() is False and suppressError is True:
        # skip "Err" message if RTC is already configured
        return False
    else:
        # otherwise, display "Err"
        tot.display().setDigitsBinary(0b01111001, 0b01010000, 0b01010000, 0)

        # wait for user to press button
        while True:
            tot.inputs().strobe()
            if tot.inputs().set() is True:
                break

        # blank display
        tot.display().setDigitsBinary(0, 0, 0, 0)
        
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

def init(tot):
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
    if tot.nic() is not None and tot.nic().isUp() is False:
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

def loop(tot):
    # state-based variables
    ticks_up_held = 0
    ticks_down_held = 0
    ticks_set_held = 0
    ticks_dst_held = 0
    ticks_since_datedisplay_pushed = 0

    brightness = tot.cvars().get(u"config.display",u"brightness")
    if not (1 <= brightness and brightness <= 8):
        brightness = 8
    tot.display().setBrightness(brightness) 

    set_and_dst_no_debounce = tot.cvars().get(u"wurthless.clock.clockmain", u"set_and_dst_no_debounce")
    disable_calendar = tot.cvars().get(u"wurthless.clock.clockmain", u"disable_calendar")

    dst_disable = tot.cvars().get(u"config.clock",u"dst_disable") 

    next_cfg_writeback = None
    cfg_writeback_delay = tot.cvars().get(u"wurthless.clock.clockmain",u"settings_write_delay")
    
    displaymode = 0
    should_rerender_display = False
    last_second = int(time.time())
    while True:
        if should_rerender_display == True:
            renderDisplay(tot, displaymode)
            should_rerender_display = False
        else:
            t = int(time.time())
            if t != last_second:
                should_rerender_display = True
                last_second = t
                
        tot.inputs().strobe()
        up_state = tot.inputs().up()
        down_state = tot.inputs().down()
        set_state = tot.inputs().set()
        dst_state = tot.inputs().dst()

        # Pressing UP changes brightness in descending order.
        # If brightness is at minimum, reset to highest brightness.
        if not up_state and ticks_up_held != 0:
            ticks_up_held = 0
        elif up_state:
            if ticks_up_held == 0:
                brightness -= 1
                if not (1 <= brightness and brightness <= 8):
                    brightness = 8
                tot.display().setBrightness(brightness) 
                tot.cvars().set(u"config.display",u"brightness",brightness)
                next_cfg_writeback = tot.rtc().getUtcTime() + cfg_writeback_delay
                ticks_up_held = 1

        # Pressing DOWN will toggle between displaymodes
        # in this order: year, month, day, time
        # If the displaymode goes off of time for a while, switch back to time.
        # DOWN does nothing if calendar mode disabled.
        if disable_calendar is False:
            if not down_state and ticks_down_held > 0:
                ticks_down_held = 0
            elif down_state:
                if ticks_down_held == 0:
                    # toggle displaymode
                    displaymode += 1
                    displaymode &= 3
                    should_rerender_display = True
                    ticks_since_datedisplay_pushed = 1
                    ticks_down_held += 1
            
            if ticks_since_datedisplay_pushed != 0:
                ticks_since_datedisplay_pushed += 1
                if ticks_since_datedisplay_pushed == 200:
                    displaymode = 0
                    should_rerender_display = True
                    ticks_since_datedisplay_pushed = 0

        # Pressing and holding SET for long enough will go to configuration mode
        # if we are allowed to configure the RTC at all
        if tot.rtc().readOnly() is False:
            if not set_state and ticks_set_held > 2:
                ticks_set_held = 0
            elif set_state:
                if ticks_set_held == 0:
                    pass

                ticks_set_held += 1

                if ticks_set_held == 255 or set_and_dst_no_debounce is True:
                    # attempt synchronization to timesource
                    if tot.timesources() is not None and tot.timesources() != []:
                        if syncTime(tot, suppressError=False) is False:
                            configMode(tot)
                    else:
                        configMode(tot)

                    ticks_set_held = 0
                    
                    # if configuration mode entered, kill any pending settings writeback
                    next_cfg_writeback = None

        # Pressing and holding DST for long enough sets/unsets DST.
        # Skip this logic if DST is explicitly disabled in config.
        if dst_disable is False:
            if not dst_state and ticks_dst_held > 2:
                ticks_dst_held = 0
            elif dst_state:
                if ticks_dst_held == 0:
                    # debugging leftover
                    pass

                ticks_dst_held += 1
                if ticks_dst_held == 255 or set_and_dst_no_debounce is True:
                    # set / unset DST flag and save cvars
                    dst = tot.cvars().get(u"config.clock",u"dst_active")
                    dst = not dst
                    tot.cvars().set(u"config.clock",u"dst_active",dst)
                    
                    next_cfg_writeback = tot.rtc().getUtcTime() + cfg_writeback_delay
                    ticks_dst_held = 0
        
        if next_cfg_writeback is not None:
            t = tot.rtc().getUtcTime()
            if next_cfg_writeback <= t:
                tot.cvars().save()
                next_cfg_writeback = None

        snooze()

def clockMain(tot):
    # if DOWN held on reset, go to burnin / demo mode
    if tot.inputs().down():
        burnin(tot)
    
    # enter webserver config mode when SET is held on reset
    force_server = tot.cvars().get(u"wurthless.clock.clockmain", u"force_server")

    tot.inputs().strobe()
    if tot.inputs().set() or force_server:
        # display "cfg"
        tot.display().setBrightness(8)
        tot.display().setDigitsBinary(0, 0b00111001, 0b01110001, 0b01111101)

        serverMain(tot)


    # the ghost of Arduino past refuses to go away
    init(tot)
    while True:
        loop(tot)
