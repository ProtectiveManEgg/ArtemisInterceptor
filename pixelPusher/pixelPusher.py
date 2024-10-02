# [ imports ] -------------------
import wifi
import json
import microcontroller as mc
import time
import builtins

from socketpool import SocketPool as socketpool
from adafruit_httpserver import Server, Request, Response, Route, GET, POST
from neopixel import NeoPixel
from asyncio import create_task, gather, run, sleep as async_sleep

# [ core ] ----------------------
old_print = print # store old print
def debugPrint(*arg, err = False): # i want the ability to disable prints later
	old_print((err and "ERROR" or "DEBUG") + " |: ", *arg)
builtins.print = debugPrint

class pixelPusher:
	ips = {
		"host": None,	# address of the local machine
		"client": None	# address of the remote connection
	}
	ports = {
		"tcp": 80,		# Artemis uses `80`
		"udp": None		# port to use for the UDP sock. Artemis sends `1872`
	}
	pixels = []

	max_buff_size = (255 * 3) + 2 # max buffer set by RGB.NET client
	
	def __init__(self, ssid, passw): # add debug flag later
		for i in range(len(self.channels)):
			if self.channels[i][1] > 0: # only init channels with leds
				self.pixels.insert(i, NeoPixel(self.channels[i][0], self.channels[i][1], auto_write = False))
				self.pixels[i].fill((0, 0, 255))
				self.pixels[i].show()
			
		print(f"Initiated {len(self.pixels)} channels")
		
		print("Attempting to connect to WIFI...")
		self.connectWLAN(ssid, passw)
		if wifi.radio.connected:
			print("Connected as: ", self.ips["host"])
			run(self.start())
		else: # shouldn't make it this far. if this never gets called, remove it
			print("Not connected!", err = True)
			self.reboot()
	
	async def start(self):
		self.pool = socketpool(wifi.radio)
		self.server = Server(self.pool, debug = True)
		
		self.udp = self.createSock(self.ips["host"], self.ports["udp"], timeout = 0.01, udp = True)
		
		self.server.add_routes([
			Route("/", [GET, POST], self.serveRoot),
			Route("/enableUDP", POST, self.enableUDP),
			Route("/disableUDP", POST, self.disableUDP),
			Route("/reset", GET, self.reset),
			Route("/config", GET, self.serveConfig),
			Route("/update", GET, self.update),
		])
		
		self.server.start(self.ips["host"], port = self.ports["tcp"])
		
		await gather( # could probably just use create_task, but this serves to remind
			create_task(self.poll())
		)
			
	# [ utilities ] -------------
	def createSock(self, ip, port, timeout = 1, udp = False):
		sock = self.pool.socket(self.pool.AF_INET, (udp == False and self.pool.SOCK_STREAM or self.pool.SOCK_DGRAM))
		sock.settimeout(timeout)
		#sock.setsockopt(self.pool.SOL_SOCKET, self.pool.SO_REUSEADDR, 1) # this may not match micropython
		return sock
		
	def connectWLAN(self, ssid, passw):
		max_tries = 10
		tried = 0
		while wifi.radio.connected == False:
			tried += 1
			if now < max:
				try:
					print("Attempting to connect WIFI...")
					wifi.radio.connect(ssid, passw)
				except OSError as e: # ConnectionError: Unknown failure 1 -- board needs to be rebooted
					pass
					#print(e, err = True)
					#self.reboot()
				finally:
					self.ips["host"] = str(wifi.radio.ipv4_address)
			else:
				print(e, err = True)
				self.reboot()
			
			time.sleep(1)

	def trueMax(self, t):
		last = 0
		for i in range(len(t)):
			if t[i][1] > last:
				last = t[i][1]
		
		return last
	
	def success(self, req, body = "", encoded = False):
		return Response(req, content_type = (encoded and "application/json" or "text/html"), body = body)
	
	def reboot(self):
		if hasattr(self, "udp"):
			self.udp.close()
		
		wifi.radio.stop_station()
		self.reset() # turn off pixels
		mc.reset() # restart the board
		
	async def poll(self):
		while True:
			try:
				self.server.poll()
				create_task(self.readUDP()) # try gathering this again. maybe it will be better now?
			except KeyboardInterrupt as e:
				print("Interrupted by user!", err = True)
				self.reboot()
		
			await async_sleep(0)
	
	async def readUDP(self):
		if self.ips["client"] is not None:
			try:
				buff = bytearray(self.buff_size)
				size, _ = self.udp.recvfrom_into(buff)
				seq, channel, b_list = buff[0], buff[1] - 1, list(buff[2:])
				
				for i in range(self.channels[channel][1]):
					self.pixels[channel][i] = (
						int(b_list[(i * 3)]* self.brightness), 		# R index / brightness
						int(b_list[(i * 3) + 1] * self.brightness), # G index / brightness
						int(b_list[(i * 3) + 2] * self.brightness) 	# B index / brightness
					)
				self.pixels[channel].show()
			except KeyboardInterrupt:
				print("Interrupted by user!")
				self.reboot()
			except OSError as e: # skip over etimedout
				pass 
		
	# [ server routes ] -------------
	def serveRoot(self, req: Request): # make this a static file and format in the variables somehow
		return self.success(req, body = f'''
			<html>
				<head>
					<title>Artemis-RGB client in CircuitPython :)</title>
				</head>
				<body>
					<h1>PixelPusher</h1>
					This device is currently running CircuitPython on a Pi Pico!<br/>
					<br/>
					Check <a href="https://github.com/ProtectiveManEgg/PixelPusher">PixelPusher</a> for more info on this project!<br/>
					Special thanks to <a href=\"https://github.com/DarthAffe/RGB.NET\">RGB.NET</a>! I based this project upon their NodeMCU Sketch!<br/>
					<br/>
					<h3>Configuration:</h3>
					<b>UDP:</b> "{self.ips["client"] is not None and "enabled (" + str(self.ports["udp"]) + ")" or "disabled"}"<br/>
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

	def enableUDP(self, req: Request):
		self.ips["client"] = req.client_address[0] # may not need these references though
		self.ports["udp"] = int(req.body)
		
		self.udp.bind((self.ips["host"], self.ports["udp"]))
		
		return self.success(req)

	def disableUDP(self, req: Request):
		self.ips["client"] = None # this is my toggle for `readUDP`
		self.udp.close()
		
		return self.success(req)

	def reset(self, req: Request = None): # should allow no request to be sent?
		for i in range(len(self.pixels)):
			self.pixels[i].fill((0, 0, 0))
			self.pixels[i].show()
		
		return (req is not None and self.success(req) or False)

	def serveConfig(self, req: Request):
		config = [
			{"channel": 1, "leds": self.channels[0][1]},
			{"channel": 2, "leds": self.channels[1][1]},
			{"channel": 3, "leds": self.channels[2][1]},
			{"channel": 4, "leds": self.channels[3][1]}
		]
		
		return self.success(req, body = json.dumps(config), encoded = True)

	def update(self, req: Request):
		# this is an alternate to the udp socket i think
		# i've never actually seen it called
		
		return self.success(req)