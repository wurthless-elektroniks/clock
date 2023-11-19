# The Most Useless Clock in the World

![TMUCITW running under curses](docs/testbench.png)

Python-based seven-segment digital clock. It is called "The Most Useless Clock in the World" because it is janky, overpriced, and tells the time and nothing else. But it is very stylish and can easily be seen across a room.

This is a rewrite of the [original TMUCITW software](https://github.com/wurthless-elektroniks/clock_v1), but aims to be much more portable and modular than the original, which only targeted ATMega328s that had a MAX7219 and DS1307. It also features the ability to synchronize time with a timesource, which is most often a NTP server accessed over Wi-Fi, but can be anything.

# How to use

* For local testing on PC: python3 run_pc.py
* For deployment on RP2040-based hardware: copy relevant ini in defaults/ to secrets, rename factory.ini, and have your RP2040 board call the appropriate function in run_pico.py
* Might be ported to ESP32 at some point, it's a bit cheaper than the Pico W

# Technical support, manual, etc.

See docs/ directory.

# License

BSD 3-clause
