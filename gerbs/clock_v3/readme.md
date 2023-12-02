# The Most Useless Clock in the World (v3)

This is the last large form factor version of TMUCITW. As it's easier to mount on a tabletop, it makes sense that people will want it. Too lazy to open Time Machine to get the old KiCad project files so I'm releasing them as is.

## Caution

* The LED driver circuit will not work with LEDs that require 3 volts or more, because it's poorly designed.
* There is no protection diode to prevent backfeeding the Pico's microUSB voltage to the mini-USB connector. If you are squeamish, bodge one on.

## Bill of Materials

* U1: Raspberry Pi Pico W
* U2: *OPTIONAL* TLV-1117-33 voltage regulator. If populated, jump JP1 to use it.
* C1/C2: Courtesy caps to help stabilize the 3v3 and 5v rails respectively.
* J1: Unpopulated. Connector exists for development purposes. 
* J2: Standard Mini USB connector.
* All transistors are NPN SOT-23
* SW1,2,3,4,5: 6mm x 6mm throughhole momentary pushbutton switches
* 112 LEDs (5mm or 3mm work)
* R1: Current limiting resistor for Q1 base; typically 2k ohms