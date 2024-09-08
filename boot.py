# sorry for bad/messy code. this script represents the alpha test

import board
import json
from rainbowio import colorwheel
from time import sleep
import wifi
import socketpool as socket
import neopixel

from adafruit_httpserver import Server, Request, Response, Websocket, GET, POST, PUT, DELETE
from asyncio import create_task, gather, run, sleep as async_sleep

# settings ------------------
ssid = "Lord Of The Pings"
passw = "#MyPr3c10us#"
# ---------------------------
led_1 = 37
led_2 = 0
led_3 = 0
led_4 = 0

ch_1 = board.GP8
ch_2 = board.GP0
ch_3 = board.GP6
ch_4 = board.GP7

pixels = neopixel.NeoPixel(ch_1, led_1, auto_write=False)
pixels.fill((255, 255, 255))
pixels.show()
# ---------------------------

def connectWLAN():
	try: # not finding wifi
		net = None
		for n in wifi.radio.start_scanning_networks():
			#print(f"SSID: {n.ssid}, Strength: {n.rssi}, Channel: {n.channel}")
			if n.ssid == ssid:
				net = n
				print("Found network. Attempting connection...")
				break
		
		wifi.radio.connect(ssid, passw) #, channel = net.channel)
		return str(wifi.radio.ipv4_address)
	except ConnectionError as e: # reboot pico when no wifi is found
		print(e)
		raise #microcontroller.reset()
addr = connectWLAN()

if addr is not None:
	print("connected as:", addr)

	pool = socket.SocketPool(wifi.radio)
	pool.socket(pool.AF_INET, pool.SOCK_STREAM)

	server = Server(pool, debug = True)
	
	udp = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
	udp.settimeout(1.5)
	cli_addr, port = None, None
	
	websocket: Websocket = None
	
	
	def sendUDP(): # jjust so i dont forget
		size, addr = s.sendto(b"hello world", (cli_addr, port))
		
	async def readUDP(): # got hung up
		global pixels
		if cli_addr is not None: # 5 seconds to allow udp packets to be sent? bad idea, works for now
			try:
				buff = bytearray(256)
				udp_size, _ =  udp.recvfrom_into(buff)
				byte_list = list(buff[0:udp_size]) # shrink buffer to actual size
				
				seq = buff[0] # sequence; not important?
				channel = buff[1] # channel of LEDs to talk to
				
				
				leds = []
				if channel == 1: # only programming one channel. make this better later
					for i in range(udp_size - 2):
						if i % 3 == 0:
							# create next index. remember offset by 2 to account for seq and buff
							leds.append((byte_list[i + 2], byte_list[i + 3], byte_list[i + 4])) # B-R-G??
							
					byte_list = None
					
					for i in range(len(leds)):
						pixels[i] = leds[i]
						#print(leds[i], pixels[i])
					pixels.show()
			
			except Exception as e:
				if e == KeyboardInterrupt:
					pixels.fill((0, 0, 0))
					pixels.show()
					print("interrupted")
				#else:
				#	print(e)
			
			
		await async_sleep(0)

	@server.route("/", [GET, POST, PUT, DELETE]) # POST?
	def handleRoot(req: Request): # hard coded port need to fix
		return Response(req, content_type = "text/plain", body = f'''
				<head>\
					<title>Artemis-RGB client in CircuitPython :)</title>\
				</head>\
				<body>\
					<h1>RGB.NET</h1>\
					This device is currently running CircuitPython on a Pi Pico!<br />\
					<br />\
					Check <a href=\"https://github.com/DarthAffe/RGB.NET\">https://github.com/DarthAffe/RGB.NET</a> for more info and the latest version of this sketch.<br />\
					<br />\
					<h3>Configuration:</h3>\
					<b>UDP:</b>\enabled (1872)<br />\
					<br />\		
					<b>Channel 1</b><br />\
					Leds: "{led_1}"<br />\
					Pin: "{ch_2}"<br />\
					<br />\
					<b>Channel 2</b><br />\
					Leds: "{led_2}"<br />\
					Pin: "{ch_2}"<br />\
					<br />\
					<b>Channel 4</b><br />\
					Leds: "{led_3}"<br />\
					Pin: "{ch_3}"<br />\
					<br />\
					<b>Channel 4</b><br />\
					Leds: "{led_4}"<br />\
					Pin: "{ch_4}"<br />\
					<br />\
				</body>\
			</html>";
			'''
		)
		
	@server.route("/enableUDP", POST)
	def enableUDP(req: Request):
		global cli_addr, port
		cli_addr, port = req.client_address[0], int(req.body)
		udp.bind((addr, port))

		return Response(req, content_type = "text/plain", body = "")
		
	@server.route("/disableUDP", [GET, POST, PUT, DELETE]) # POST?
	def disableUDP(req: Request):
		global cli_addr
		cli_addr = None # could use this to check if "enabled"
		udp.close()
	
		return Response(req, content_type = "text/plain", body = "")
	
	@server.route("/reset", GET)
	def handleReset(req: Request):
		pixels.fill((0, 0, 0)) # add the other channels later
		pixels.show()
		
		return Response(req, content_type = "text/plain", body = "")
	
	@server.route("/config", GET)
	def handleConfig(req: Request): # use built in json translation for the table
		channels = [
			{
				"channel": 1,
				"leds": led_1
			},
			{
				"channel": 2,
				"leds": led_2
			},
			{
				"channel": 3,
				"leds": led_3
			},
			{
				"channel": 4,
				"leds": led_4
			}
		]
		return Response(req, content_type = "text/plain", body = json.dumps(channels))

	@server.route("/update", [GET, POST, PUT, DELETE]) # POST?
	def handleUpdate(req: Request):
		# dunno really what this is for?
		
		return Response(req, content_type = "text/plain", body = json.dumps(channels))
	
	# ---------
			
	async def polling(): # need to manually poll
		while True:
			try:
				server.poll()
				create_task(readUDP())
			except KeyboardInterrupt:
				raise print("ERROR:", e)
				
			await async_sleep(0)

	async def main():
		#server.serve_forever(host = addr, port = 80, poll_interval = 0.1) blocking
		server.start(addr, port = 80)
		await gather(
			create_task(polling()),
		)
	
	run(main())
