
# PixelPusher
This is a client for Artemis-RGB designed to drive led strips. Because this project utilizes WIFI, it can realistically drive a strip of LEDs anywhere from inside your PC case to under your desk. Only limit is power source! What inspired this project was RGB.NET for the Pi Pico W. The firmware didn't work for me, and neither did the config. Either way, this project is a deconstruction of [DarthAffe](https://github.com/DarthAffe)'s [NodeMCU sketch](https://github.com/DarthAffe/RGB.NET/blob/master/RGB.NET.Devices.WS281X/Sketches/RGB.NET_NodeMCU.ino). I wanted the simplicity of using Python, and CircuitPython seemed like a good choice.

DarthAffe _did_ test if it worked on a Pico W and had success. It's likely just my environment. His firmware is _much_ simpler than this project. PixelPusher's creation is just for my own fun (and potentially yours).

## Dependencies 
**I included libraries, but verify correct version**
- adafruit_httpserver
- asyncio
- neopixel
- adafruit_pixelbuf (pre-requisite for neopixel)
- adafruit_ticks (pre-requisite for asyncio)

## Installation
Copy `code.py` to your CircuitPython "drive," and install the above dependancies to the `/lib` folder.
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
- 3v3 (OUT) not 3v3_EN
- Pi 0 version being experimented with. Uses CPython and different modules and procedures
- make some sort of insulated backplate or mounting plate for the Pi
- test more than 1 channel (lol)
- bench the time it takes to boot to adjust the sleep before `init`. trying to connect wifi before this time will result in errno 1 (Unknown failure). to test this, i set a 5 second sleep and it booted fine
- moved strip creation before wifi start to have a visual cue that the script hasn't errored before attempt to connect wifi
- write a file editor in `debugger` to write logs for a USB-less boot

## Test-bench Circuit Drawing [Updated]
![now](https://img001.prntscr.com/file/img001/TrDUJjuISe-vrZhdo60_sQ.png)
Thanks to `DarthAffe` and `Senpo` for why to use a resistor on the data line and a cap before the strip.

Molex power is prototyped and _does_ work. For testing, I will only be using the barrel connector in the off-chance that something goes wrong, I'd rather blow up the cheap external supply. Included the Molex connector in the drawing. Swap the place of the barrel connector for the final circuit. Powering from VSYS _does_ work. Save to `code.py` and reboot.
