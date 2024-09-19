
# PixelPusher
This is a client for Artemis-RGB designed to drive led strips. Because this project utilizes WIFI, it can realistically drive a strip of LEDs anywhere from inside your PC case to under your desk. Only limit is power source! What inspired this project was RGB.NET for the Pi Pico W. The firmware didn't work for me, and neither did the config. Either way, this project is a deconstruction of [DarthAffe](https://github.com/DarthAffe)'s [NodeMCU sketch](https://github.com/DarthAffe/RGB.NET/blob/master/RGB.NET.Devices.WS281X/Sketches/RGB.NET_NodeMCU.ino). I wanted the simplicity of using Python, and CircuitPython seemed like a good choice.

## Dependencies 
**I included libraries, but verify correct version**
- adafruit_httpserver
- asyncio
- neopixel
- adafruit_pixelbuf (pre-requisite for neopixel)
- adafruit_ticks (pre-requisite for asyncio)

## Installation
Copy `boot.py` to your CircuitPython "drive," and install the above dependancies to the `/lib` folder.
These instructions are pretty bare and have the expectation of the user being already familiar.

I recommend the use of [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup) just out of its ease of use. To install the modules, simply run `circup install pkg_name`. Installing the pre-requisites are only necessary if installing [manually](https://circuitpython.org/libraries).

- Once dependancies are installed, reboot your Pi Pico W! CircuitPython will start the HTTP server at boot.

- Next, go to the Artemis client, and click settings. Switch to the Plugins tab and search for `ws281x`. Install `WS281x Devices`.

- Once installed, click enable and open settings. 
- Add device
    - Display name can be whatever you want
    - Device type: `ESP 8266`
    - Hostname is the IPv4 address of your Pi

Any issues with the program can be resolved with a reboot of the Pi, and reloading the plugin in Artemis. The Pi does have a periodic issue with connecting to WIFI where it provides an unknown connection error (errno 1). Not sure exactly what was causing it, but I seemed to have handled it. 

## Notes to self:
- Pi 0 version being experimented with. Uses CPython and different modules and procedures
- figure out what is causing the intermittent flickering! the level shifter did get wet!
- make some sort of insulated backplate or mounting plate for the Pi
- test more than 1 channel (lol)
- should really add a check to make sure the buffer is actually set with new data. this could theoretically be causing the flickering if the UDP socket is reading no data and setting the empty bytes

## Test-bench Circuit Drawing
![now](https://img001.prntscr.com/file/img001/TqQdUkBRTA-IBeLW4pmjpw.png)
Thanks to `Senpo` on Discord for the heads up that the Pico probably can't drive too many LEDs without the shifter. Scratch that design!
MOLEX power won't be prototyped until I get around to buying the new case and pull out the PSU.
