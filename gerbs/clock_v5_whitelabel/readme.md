# The Most Useless Clock in the World (v5, white label)

Unbranded RPi Pico W-based clock for your clockey enjoyment. Production version still has to be tested. You get absolutely no support for these, and I won't bother correcting any hardware bugs that come with this release. The Pico era of TMUCITW is over. It's time to move on.

## Parts, BoM, what haves ya

* U1: Raspberry Pi Pico W, will also accomodate the Pico and Pico H
* U2: BCR420UW6 constant current device, SOT-26 footprint
* R1: Sense resistor for BCR420UW6 (value varies); 1210 footprint
* R2/R3: 5.1k pullup resistors to enable USB-C power, 0603 footprint
* Q1, Q2, Q3, Q4, Q5, Q7: Dual NPN transistors, E1/B1/C2 pinout, SOT-363 footprint
* Q6: NPN transistor, BEC pinout, SOT-23 footprint
* RN1, RN2: 220 ohm segment isolating/current limiting resistors, 4x1206 footprint
* D113: 1206 input protection diode so idiots do not backfeed micro USB power to a USB-C host
* C1: 100 uF courtesy cap, 1206 footprint
* SW1, SW2, SW3, SW4, SW5: 6x6mm tactile switches
* And, most importantly, 112 LEDs, 5mm or 3mm both work
