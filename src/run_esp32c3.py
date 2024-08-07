"""
This is split out to its own file possibly for historical purposes.
run_esp32.py was getting too big.

# ESP32-C3-WROOM-02 support is very limited.
# almost all accessible GPIOs are taken up by the LED matrix.
# it does work, but not reliable enough to be considered usable (yet).
def runEsp32C3Wroom02():
    tot = ToT()

    cvars = Cvars()
    writer = TokenedCvarWriter()

    # "factory" is the factory defaults
    writer.addPreflight(u"secrets/factory.ini")
    
    # "guid" is device-specific stuff (serial number, device name, etc.)
    writer.addPreflight(u"secrets/guid.ini")

    cvars.setWriter(writer)

    cvars.load()
    tot.setCvars( cvars )

    # BEFORE the LED matrix starts up, check pin 0 status.
    # we don't have enough I/Os to allow the user to re-enter config mode!
    bootpin = Pin(0, Pin.IN, Pin.PULL_UP)
    if bootpin.value() == 0:
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.setDisplay( Esp32MaskDisplay(tot) )
    tot.setInputs( NullInputs() )
    tot.setRtc( MicropythonRTC() )

    # display INIT
    tot.display().setDigitsBinary(0b00000110, 0b00110111, 0b00000110, 0b01111000)

    # install NIC and NTP timesource
    tot.setNic( MicropythonWifiNic(tot) )
    tot.setTimeSources( [ NtpTimeSource(tot) ] )

    # force server mode if user hasn't configured wifi yet
    if tot.cvars().get(u"config.nic",u"wifi_ap_name") == u"":
        tot.cvars().set(u"wurthless.clock.clockmain", u"force_server", True)

    tot.finalize()
    clockMain(tot)

"""