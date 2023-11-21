# The Most Useless Clock in the World: The User Manual

Congratulations! You were dumb or unlucky enough to buy, acquire, or otherwise use The Most Useless Clock in the World. You now have a janky, overpriced and unreliable clock that doesn't do much other than tell the time. But it does look stylish when viewed across a room.

**If you're an end-user, this documentation is for you.** If you're just someone who wants to use this code as part of their own project (*who would?*), then it will still be useful in a way. However, most of the technical docs, if any, will live in the sourcecode.

## Why the hell would you do something like this?

Building a clock, or some such basic-yet-useful device, is a typical beginners' electronics project which I would highly recommend to anyone looking to start out in the hobby. It teaches the following:

* Electronics
* Soldering, particularly for surface mount components
* Circuit design
* Embedded systems software development
* Cost-reduction techniques

So yeah, this is a dumb hobby project that I keep going back to because it's interesting.

## Hardware revisions

This section only applies to those who have a würthless elektroniks-branded TMUCITW. If you're just checking out the code for your own use, you can at least appreciate the pretty pictures.

### The original prototype

![](proto.jpeg)

It's nice to look at.

### Version 1

![](v1.jpeg)

**Version 1** is something I don't support anymore. It ran on ATMega328-based hardware with a MAX7219 driving the display and a DS1307 for RTC. As you can tell, that's extremely expensive and was a motivator for remaking the clock on much cheaper hardware. Much of the documentation below should apply to how it behaves. In case you give a shit, only three of these exist in the wild, although there could possibly be more if someone dumb enough to do so builds more of them using [the publicly available Gerbers and sourcecode](https://github.com/wurthless-elektroniks/clock_v1).

### Version 2

![](v2.jpeg)

**Version 2** (*double the uselessness, double the destruction*) is the first RP2040-based version, now using the standard stylish black solder mask. This board will typically come with bodges applied; while it's ugly, it's necessary for the clock to function at all. Originally, DST and the master PWM transistor would be controlled entirely in software, but this was decided against because it would add code complexity and would not be safe or reliable (that master output control transistor has gone up in smoke on me several times during testing.)

### Version 3

![](v3.jpeg)

**Version 3** (*for those about to clock... we salute you*) fixes the issues with v2, changes to a mini-USB port for power and has a bigger expansion port. It also has space for a TLV-1117-33 voltage regulator, but it is not populated as the Pico's built-in 3v3 voltage regulator works nicely enough.

### Version 4

**Version 4** (*rock out with your USB-C clock out*) I haven't determined the fate of yet.

### Version 5

**Version 5** (working title: *my clock is bigger than yours!*) I also haven't determined the fate of yet.

### TMUCITW Junior

**TMUCITW Junior** is also yet to be decided on. It will almost certainly run on cheaper ESP32-based hardware and only support 12-hour time.

## Initial Setup

### For Wi-Fi-enabled clocks:

**IF YOUR CLOCK HAS WI-FI SUPPORT**, the first thing that should be displayed is the letters "CFG". This means that the clock is starting up in configuration mode. Using a Wi-Fi compatible device, connect to the network labelled TMUCITW. If prompted for a network password, enter "wurthless" (no quotes!).

Then open your web browser to [http://192.168.4.1]. If successful, you'll see a page like this:

![](configpage.png)

Here's what to enter:

* "wifi accesspoint": The name of your Wi-Fi network. As the page notes, this needs to be a 2.4 GHz Wi-Fi network, as 5 GHz networks are not supported. When in doubt, check your router settings.
* "wifi password": The password for the given network. **This is required**. If your Wi-Fi network is not password protected, you're a bozo.
* "timezone": Your timezone as a UTC offset. **In regions that obey Daylight Savings Time, this is the UTC offset when DST is not in effect.**
* "dst adjust": Whether to adjust for DST. If set to "off", DST will be turned off. If set to "on", DST will be turned on. **In regions that do not observe Daylight Savings Time, you should set this to "disable dst".**

Press "save settings" to generate the bug report you will be submitting to me when it inevitably crashes. But if it doesn't crash, then congratulations, your clock is now set up. Press RESET on your clock, and it should connect to the Internet, grab the current time, and display it. Hooray!

### Manual configuration mode:

The Most Useless Clock in the World provides a manual configuration mode in the event that it is unable to synchronized to an external timesource.

If your clock boots to a message that says "Err", it was not able to synchronize to a time source, either because the Wi-Fi network is down, or the connection to the time server failed. Unfortunately, this is just what happens because the NTP servers rate-limit their clients. Wait a few seconds and press RESET. If it still won't connect to the network, hold SET until the display clears, then release SET. You'll be in manual configuration mode.

If your clock doesn't have any time sources to read from, and the clock is not already set (or loses its configuration because the battery dies), it will boot straight to manual configuration mode.

In manual configuration mode, the clock typically prompts for inputs in the following order: **year, month, day, hour, minute**. Press UP or DOWN to change settings, and press SET to confirm and move on to the next one. If you mess something up, don't fret, you can always enter configuration mode again once the clock is set.

**If the Daylight Savings Time feature is not disabled,** the last setting in manual configuration mode will be DST. The clock will display "DST ON" or "DST OFF". Press UP/DOWN to toggle the setting. This setting should reflect whether Daylight Savings Time is effect in your region or not. Press SET to confirm the setting.

## Normal operation state

The clock displays the current time. Duh!

However, the pushbuttons on the front will still be active. Here's what they do.

* Pressing **UP** will change the brightness setting. It will decrease with each push until it reaches its minimum setting, after which it resets to the highest brightness.
* Pressing **DOWN** will toggle between the current time, year, month, and day. After a while, the clock resets to displaying the current time.
* Holding **SET** will reconfigure the current time. If the clock is configured to synchronize time (e.g., over Wi-Fi), it will do so. In all other situations, this will send the clock back to manual configuration mode.
* Holding **DST**, **if the Daylight Savings Time feature is not disabled,** will toggle DST. 
* Pressing **RESET** at any time will force the clock to reboot.

## Quality Assurance Policy

At würthless elektroniks, we can assure you that the quality of our products is terrible. However, we try to keep our customers happy because otherwise we can't make money. If your clock dies a premature death, please get in contact with us. Once we take ten minutes to laugh at your misfortune, we'll be glad to offer a replacement or any assistance. If there's a serial number on your clock, please have it handy!

Remember: **with würthless elektroniks, dissatisfaction is guaranteed or your money back!** (*NOTE: We do not offer refunds.*)
