
# PixelPusher
This project is a deconstruction of [DarthAffe's](https://github.com/DarthAffe) [NodeMCU sketch](https://github.com/DarthAffe/RGB.NET/blob/master/RGB.NET.Devices.WS281X/Sketches/RGB.NET_NodeMCU.ino). I wanted the simplicity of using Python, and CircuitPython seemed like a good choice.

This is a client for [Artemis-RGB](https://artemis-rgb.com/) designed to drive some led strips. Because this project utilizes WIFI, it can realistically drive a strip of LEDs anywhere in your home. Only limit is power source! What inspired this project was RGB.NET for the Pi Pico W. The firmware didn't work for me, and neither did the config. DarthAffe _did_ confirm it works with a Pico W. For anybody interested, [go check it out!](https://github.com/DarthAffe/RGB.NET-PicoPi)

## Dependencies 
<b>These modules can be installed manually or via [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup).</b>
- adafruit_httpserver
- neopixel
- asyncio

## Configuration
- Go to the Artemis client, and click settings. Switch to the Plugins tab and search for `WS281x`. Install `WS281x Devices`.
- Once installed, click enable and open settings. 
- Add device
    - Display name can be whatever you want
    - Device type: `ESP 8266`
    - Hostname is the IPv4 address of your Pi
 
## Usage
If less than 4 channels are sent, it will fill the list with empty channels. I haven't tested running more than 1, but if Artemis allows it, you should be able to add more?

Example `code.py`:
```python
from pixelPusher import pusher
import board

channels = [			# max channels 4
	[board.GP0, 50],	#gpio_pin, num_leds
	[board.GP8, 50]
]
brightness = 100		# pixelPusher defaults to 50% brightness

#pusher(ssid: str, passw: str, brightness: int = 50, channels: list = None)
pusher("awesome wifi", "password", brightness = brightness, channels = channels)
```

## Notes to self:
- 3v3 (OUT) not 3v3_EN
- make some sort of insulated backplate or mounting plate for the Pi
- test more than 1 channel (lol)

## Test-bench Circuit Drawing [Updated]
<b>Will update schematic when I get to soldering and mounting.</b>
![now](https://img001.prntscr.com/file/img001/TrDUJjuISe-vrZhdo60_sQ.png)
