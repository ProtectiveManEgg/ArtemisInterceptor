# [ imports ] -------------------
import wifi
import board
import json
import socketpool
import microcontroller

from adafruit_httpserver import Server, Request, Response, Route, GET, POST
from neopixel import NeoPixel
from asyncio import create_task, gather, run, sleep as async_sleep
# [ imports ] -------------------

# [ settings ] ------------------
ssid = "ssid"
passw = "passw"

channels = [
	[board.GP22, 37], # change board.GP6 to board.D8 for a pi other than a pico
	[board.GP0, 0],
	[board.GP5, 0],
	[board.GP6, 0]
]
brightness = 50 # 50%

debug = True # enable this if problems arise
# [ settings ] ------------------

# [ pre-define ] ----------------
max_buffer_size = (255 * 3) + 2 # max buffer set by RGB.NET client
buff_size = 0

remote_ip = None		  # address of the remote connection
udp_port = None			  # port to use for the UDP sock. Artemis sends `1872`
http_port = 80			  # Artemis uses `80`
host_ip = None			  # address of the local machine

pool = socketpool.SocketPool(wifi.radio)
udp = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
udp.settimeout(0.01)

server = Server(pool, debug = True)
pixels = []
# [ pre-define ] ----------------

# [ server routes ] -------------
def handleRoot(req: Request):
	return success(req, body = f'''
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
				<b>UDP:</b> "{remote_ip is not None and "enabled (" + str(udp_port) + ")" or "disabled"}"<br/>
				<br/>
				<b>Channel 1</b><br/>
				Leds: "{channels[0][1]}"<br/>
				Pin: "{channels[0][0]}"<br/>
				<br/>
				<b>Channel 2</b><br/>
				Leds: "{channels[1][1]}"<br/>
				Pin: "{channels[1][0]}"<br/>
				<br/>
				<b>Channel 4</b><br/>
				Leds: "{channels[2][1]}"<br/>
				Pin: "{channels[2][0]}"<br/>
				<br/>
				<b>Channel 4</b><br/>
				Leds: "{channels[3][1]}"<br/>
				Pin: "{channels[3][0]}"<br/>
				<br/>
			</body>
		</html>";
	''')

def enableUDP(req: Request):
	global remote_ip
	global udp_port
	remote_ip = req.client_address[0]
	udp_port = int(req.body)
	
	udp.bind((host_ip, udp_port))
	
	return success(req)

def disableUDP(req: Request):
	remote_ip = None # this is my toggle for `readUDP`
	udp.close()
	
	return success(req)

def handleReset(req: Request = None): # should allow no request to be sent?
	for i in range(len(pixels)):
		pixels[i].fill((0, 0, 0))
		pixels[i].show()
	
	return (req is not None and success(req) or False)

def handleConfig(req: Request):
	config = [
		{"channel": 1, "leds": channels[0][1]},
		{"channel": 2, "leds": channels[1][1]},
		{"channel": 3, "leds": channels[2][1]},
		{"channel": 4, "leds": channels[3][1]}
	]
	
	return success(req, body = json.dumps(config), json = True)

def handleUpdate(req: Request):
	# this is an alternate to the udp socket i think
	# i've never actually seen it called
	
	return success(req)
# [ server routes ] -------------

# [ functions ] -----------------
def debugger(*arg, prefix = None): # maybe make this write out to a log file
	if debug:
		print((prefix is None and "[DEBUG]:" or "[ERROR]:"), *arg)

def trueMax(t):
	last = 0
	for i in range(len(channels)):
		if channels[i][1] > last:
			last = channels[i][1]
			
	return last

async def init():
	global brightness
	global pixels
	global buff_size
	global host_ip

	brightness /= 100
	
	buff_size = (trueMax(channels) * 3) + 2 # this is more useful and respective of resources.  (num_leds * RGB) + headers
	if buff_size > max_buffer_size:
		debugger(f"Too many LEDs: {(max_buffer_size - 2) / 3} / {(buff_size - 2) / 3}")
		return False
	
	host_ip = connectWLAN()
	
	debugger("Local IP:", host_ip)
	
	for i in range(len(channels)):
		if channels[i][1] > 0: # only initialize channels with leds
			pixels.insert(i, NeoPixel(channels[i][0], channels[i][1], auto_write = False))

			pixels[i].fill((0, 255, 0))
			pixels[i].show()
		
	debugger("Channels initiated:", len(pixels))
	
	if host_ip:
		server.add_routes([
			Route("/", POST, handleRoot),
			Route("/enableUDP", POST, enableUDP),
			Route("/disableUDP", POST, disableUDP),
			Route("/reset", GET, handleReset),
			Route("/config", GET, handleConfig),
			Route("/update", POST, handleUpdate),
		])	
		
		server.start(host_ip, port = http_port)
		await gather(
			create_task(poll())
		)
		
		return True
	else:
		debugger("Not connection found!")
		return False
		


async def poll():
	while True:
		try:
			server.poll()
			create_task(readUDP()) # same thread will cause it to hang
		except Exception as e:
			if e == KeyboardInterrupt:
				handleReset()
				raise debugger("Interrupted by user", prefix = True)
		
		await async_sleep(0)

def connectWLAN():
	try:
		wifi.radio.connect(ssid, passw) 
		return str(wifi.radio.ipv4_address)
	except ConnectionError as e:
		handleReset()
		debugger(e, prefix = True)
		raise

def success(req, body = "", json = False):
	return Response(req, content_type = (json and "application/json" or "text/html"), body = body)

async def readUDP():
	if remote_ip is not None:
		try:
			buff = bytearray(buff_size)
			size, _ = udp.recvfrom_into(buff)
			seq, channel, bytes = buff[0], buff[1] - 1, list(buff[2:size])
			
			for i in range(channels[channel][1]):
				pixels[channel][i] = (
					int(bytes[(i * 3)] * brightness),     # R index / brightness
					int(bytes[(i * 3) + 1] * brightness), # G index / brightness
					int(bytes[(i * 3) + 2] * brightness)  # B index / brightness
				)
			
			pixels[channel].show()
		
		except Exception as e: # this stops ETIMEDOUT from crashing the server
			if e == KeyboardInterrupt:
				handleReset()
				debugger("Interrupted by user", prefix = True)
		
	await async_sleep(0)
# [ functions ] -----------------

# [ init ] ----------------------
if __name__ == "__main__":
	success = run(init())
	if not success:
		debugger("Rebooting...")
		microcontroller.reset()
		
