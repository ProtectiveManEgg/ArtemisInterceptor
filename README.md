I started this project because the RGB.NET PicoPi uf2 didn't work for me at all. The only part that worked was using Zadig to make the device reachable (lol).

ArtemisRGB allows you to use a NodeMCU (sketch provided by DarthAffe). Deconstructing that sketch, and a lot of debugging later... The alpha version is brought to life.

My todo list:
  - Erase all the commented prints
  - Properly sort different channels/LEDs, though idk how well the pico can hold up 4 channels of LEDs
  - Properly format `handleRoot`'s `Response` body
  - Localize any variables that don't need to be global (hopefully reduce RAM consumption)
  - Figure out what "/update" is for since in my tests it have never ONCE been called
  - Proper error handling! This is a must!!!
  - Modularize this to be more like a library? Possibly make it a library???

  - default ports set by artemis
      - http: `80`
      - socket: `1872` defined in `/enableUDP`

  ```python #todo
channels = [ # sent during initiation
  [board.GP8, 37],
  [board.GP0, 0],
  [board.GP5, 0]
  [board.GP6, 0]
]

class pixelPusher("SSID", "PASSWORD", channels, debug = False):
  self.client_ip = "/enableUDP" req.client_address
  self.port = "/enableUDP" int(req.body)
  self.pool = SocketPool(self.host)
  self.sock = None # set through "/enableUDP" and use it to determine if socket is active
  self.host = connectWLAN() # call this and set before self.pool

  def debugger(*args):
    if debug == True: # a flag to not bloat the console during regular use
      print("DEBUG: ", *args)
  
  def udpRead(): # return read packets to calling function to process
    sequence = buff[0]
    channel = buff[1]
    data = bytes[2:]

    retuen sequence, channel, data
```
