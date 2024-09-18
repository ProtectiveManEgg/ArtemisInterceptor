import wifi
import socketpool
import json
from time import sleep
from adafruit_httpserver import Server, Request, Response, GET, POST
from neopixel import NeoPixel
from asyncio import create_task, gather, run, sleep as async_sleep

# see if i can run the server from here too. 
# it would make it much easier if i could
#
# this is just to retrieve the data sent from Artemis.
# handle _everything_ else outside of this module
#
# not totally done. this is just the beginning

class pixelPusher:
	def __init__(self, ssid, passw, channels, debug = False):
		self.debug = debug
		self.channels = channels
		self.pixels = []

		self.client_ip = None # set by "/enableUDP"
		self.udpPort = None # set by "/enableUDP"
		self.httpPort = 80 # default set by Artemis. cannot change!
			
		self.host = self.connectWLAN(ssid, passw)
		if self.host is None:
			print("No network found...")
			return
		else:
			print("Connected as: ", self.host)
			self.pool = socketpool.SocketPool(wifi.radio)

			self.sock = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_DGRAM)
			self.sock.settimeout(2) # bench this time and get it as low as possible
			
			server = Server(self.pool, debug = self.debug) # dont need it to be inside self
			server.start(self.host, port = self.httpPort)
			
			@server.route("/", POST)
			def handleRoot(req: Request): # hopefully that atrocious string format works
				return Response(req, content_type = "text/plain", body = f'''
						<head>
							<title>Artemis-RGB client in CircuitPython :)</title>
						</head>
						<body>
							<h1>PixelPusher</h1>
							This device is currently running CircuitPython on a Pi Pico!<br/>
							<br/>
							Check <a href=\"https://github.com/ProtectiveManEgg/PixelPusher/tree/v2\">PixelPusher</a> for more info on this project!<br/>
							Special thanks to <a href=\"https://github.com/DarthAffe/RGB.NET\">RGB.NET</a>! I based this project upon their NodeMCU Sketch!<br/>
							<br/>
							<h3>Configuration:</h3>
							<b>UDP:</b>{self.client_ip is not None and "enabled (1872)" or "disabled"}<br/>
							<br/>
							<b>Channel 1</b><br/>
							Leds: "{self.channels[0][1]}"<br/>
							Pin: "{self.channels[0][0]}"<br/>
							<br/>
							<b>Channel 2</b><br/>
							Leds: "{self.channels[1][1]}"<br/>
							Pin: "{self.channels[1][0]}"<br/>
							<br/>
							<b>Channel 4</b><br/>
							Leds: "{self.channels[2][1]}"<br/>
							Pin: "{self.channels[2][0]}"<br/>
							<br/>
							<b>Channel 4</b><br/>
							Leds: "{self.channels[3][1]}"<br/>
							Pin: "{self.channels[3][0]}"<br/>
							<br/>
						</body>
					</html>";
				''')

			@server.route("/config", GET)
			def handleConfig(req: Request):
				config = [
					{"channel": 1, "leds": self.channels[0][1]},
					{"channel": 2, "leds": self.channels[1][1]},
					{"channel": 3, "leds": self.channels[2][1]},
					{"channel": 4, "leds": self.channels[3][1]}
				]
				
				return Response(req, content_type = "text/plain", body = json.dumps(config))

			@server.route("/enableUDP", POST)
			def enableUDP(req: Request):
				self.client_ip, self.udpPort = req.client_address[0], int(req.body)
				self.sock.bind((self.client_ip, self.udpPort))

				return Response(req, content_type = "text/plain", body = "")

			@server.route("/disableUDP", POST) # POST? I haven't seen this called yet
			def disableUDP(req: Request):
				self.client_ip = None
				self.sock.close()

				return Response(req, content_type = "text/plain", body = "")

			@server.route("/reset", GET)
			def handleReset(req: Request):
				for i in range(len(self.pixels)):
					self.pixels[i].fill((0, 0, 0))
					self.pixels[i].show()

				return Response(req, content_type = "text/plain", body = "")

			@server.route("/update", POST) # POST? I haven't seen this called yet
			def handleUpdate(req: Request):
				# looks like an alternative to the UDP sock. it's never been called on my end, so idk if this is worth spending time to implement

				return Response(req, content_type = "text/plain", body = "")
			
			async def poll():
				while True:
					server.poll()
					if self.client_ip is not None:
						try:
							#create_task(self.readUDP())
							buff = bytearray(256)
							size, _ = self.sock.recvfrom_into(buff)
							
							print(size, buff)
							
						except Exception as e:
							if e == KeyboardInterrupt:
								pixels.fill((0, 0, 0))
								pixels.show()
								print("interrupted")
							else:
								print(e)
						
					await async_sleep(0)
				
			async def startpoll():
				await gather(
					create_task(poll())
				)
				
			run(startpoll())
			
		for i in range(len(self.channels)):
			if self.channels[i][1] > 0: # dont init a channel if it has no leds attached
				self.pixels.append(NeoPixel(self.channels[i][0], self.channels[i][1], auto_write = False))
				self.pixels[i].fill((255, 255, 255)) # init each channel as it's created. makes it easier to spot a bad strip at boot
				self.pixels[i].show()

	def debugger(self, *args): # properly format the args into a string
		if self.debug == True:
			print(args)

	def connectWLAN(self, ssid, passw):
		network = None
		self.debugger("Scanning for networks...")
		for n in wifi.radio.start_scanning_networks(): # bench connection times. this may be unnecessary
			self.debugger(f"{n.ssid} [{n.channel}] | {n.rssi}")
			if n.ssid == ssid:
				self.debugger("Found network. Attempting connection...")
				network = n
				break
   
		try: # double check if ConnectionError is the exception I'm looking for
			wifi.radio.connect(ssid, passw, channel = network.channel) # using channel is supposed to make connecting faster?
			return str(wifi.radio.ipv4_address)
		except ConnectionError as e:
			self.debugger(e)
			return None

	async def readUDP(self):
		if self.client_ip is not None: # if UDP is enabled
			buff = bytearray(2 + (255 * 3)) # [256] i believe this is whats set in RGB.NET NodeMCU sketch; double check although it doesn't really matter
			size, _ = self.sock.recvfrom_into(buff)
			
			self.debugger(size, _)
			buff = buff[0:size]
			# buff[0] = sequence
			# buff[1] = channel
			# buff[2:] = led settings
			
			for i in buff[2:]:
				if i % 3:
					pixels[buff[1] - 1].fill(buff[i], buff[i + 1], buff[i + 2]) # pixel order is B-R-G?
			
			pixels[buff[1] - 1].show()
			
			''' ERROR
			192.168.2.11 -- "GET /reset" 43 -- "200 OK" 83 -- 219ms
			Traceback (most recent call last):
			  File "asyncio/core.py", line 261, in run_until_complete
			  File "/lib/pixelpusher.py", line 162, in readUDP
			OSError: [Errno 116] ETIMEDOUT
			'''