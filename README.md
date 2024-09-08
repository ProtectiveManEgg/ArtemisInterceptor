I started this project because the RGB.NET PicoPi uf2 didn't work for me at all. The only part that worked was using Zadig to make the device reachable (lol). This isn't really an interceptor... More of just a reader. Interceptor just sounded cool (also lol)... I plan to rename it later.

ArtemisRGB allows you to use a NodeMCU (sketch provided by DarthAffe). Deconstructing that sketch, and a lot of debugging later... The alpha version is brought to life.

My todo list:
  - Erase all the commented prints
  - Properly sort different channels/LEDs, though idk how well the pico can hold up 4 channels of LEDs
  - Properly format `handleRoot`'s `Response` body
  - Localize any variables that don't need to be global (hopefully reduce RAM consumption)
  - Figure out what "/update" is for since in my tests it have never ONCE been called
  - Proper error handling! This is a must!!!
  - Modularize this to be more like a library? Possibly make it a library???
