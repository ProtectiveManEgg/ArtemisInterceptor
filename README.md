
# PixelPusher
This is a client for Artemis-RGB designed to drive led strips. Because this project utilizes WIFI, it can realistically drive a strip of LEDs anywhere from inside your PC case to under your desk. Only limit is power source! What inspired this project was RGB.NET for the Pi Pico. The firmware didn't work for me, and neither did the config. Either way, this project is a deconstruction of [DarthAffe](https://github.com/DarthAffe)'s [NodeMCU sketch](https://github.com/DarthAffe/RGB.NET/blob/master/RGB.NET.Devices.WS281X/Sketches/RGB.NET_NodeMCU.ino). I wanted the simplicity of using Python, and CircuitPython seemed like a good choice.

## Dependencies 
**I included libraries, but verify correct version**
- adafruit_httpserver
- asyncio
- neopixel
- adafruit_pixelbuf (pre-requisite for neopixel)
- adafruit_ticks (pre-requisite for asyncio)

## Installation
Copy `boot.py` to your CircuitPython "drive," and install the above dependancies to the `/lib` folder.

I recommend the use of [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup) just out of its ease of use. To install the modules, simply run `circup install pkg_name`. Installing the pre-requisites are only necessary if installing [manually](https://circuitpython.org/libraries).

## Notes to self:
- line 200 needs a better comment. ETIMEDOUT _should_ be fixed. Exception serves as a catch _just in case_.
- Pi 0 version being experimented with. Uses CPython and different modules and procedures
- drive 12v from PSU molex!
