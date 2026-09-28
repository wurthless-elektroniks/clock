# IN-12 tubes board, version 2

Pretty much just v1 with optional Zeners for protection. The final high voltage connector type is still to be determined.

A few polite notes:

- The 40-pin ribbon connector carries base current to the transistors ONLY. Grounding is accomplished through the high voltage
  connection, and through ring terminals pressed against the mounting holes. Improper grounding will cause problems, so be careful.
- The base current limiting resistors are on the control board, and not this board. Shorting the base of the transistors to 3v3
  will certainly cause kablooies.
- This board can take MMBT42 and FMMT497TA transistors. MMBT42s can work but you might be pushing them a little over their
  power limit.
- The Zeners are optional; I likely won't be populating them. They're just there so that you can stick a 180v Zener for overvoltage
  protection on the anodes.
- The IN-12 tubes are meant to be soldered to the board for maximum cheapness. A lot of Nixies you'll find on eBay are pulls,
  so they should take solder well.
- If you wish to socket the tubes, you can use PC pin receptacles with this board. Socket pin measurements should be: pin diameter
  circa 1mm, pin length circa 5mm, mounting hole diameter approx 1.1mm. Tail length doesn't really matter as long as it fits the board.

Pinout is simple. Even-odd pinout, pin 1 = V1 digit 0, pin 2 = V3 digit 0, etc.
