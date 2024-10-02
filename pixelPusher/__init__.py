from .pixelPusher import pixelPusher

def pusher(ssid, passw, brightness = 50, channels = None):
	# default brightness at 50%
	if channels is None:
		raise print("Channels not set!", err = True)
		
	if len(channels) < 4:
		for i in range(4 - len(channels)):
			channels.insert(len(channels) + i, [None, 0])
	print(channels)
	
	pixelPusher.channels = channels
	pixelPusher.brightness = (brightness / 100)
	pixelPusher.buff_size = (pixelPusher.trueMax(pixelPusher, channels) * 3) + 2
	
	if pixelPusher.buff_size > pixelPusher.max_buff_size:
		raise print(f"Too many LEDs: {(pixelPusher.buff_size - 2) / 3} / {(pixelPusher.max_buff_size - 2) / 3}", err = True)
	
	pixelPusher(ssid, passw)