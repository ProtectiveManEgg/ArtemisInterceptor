import network
import socket
import asyncio
import machine
import json

from neopixel import NeoPixel

# -- [ settings ] --
ssid = "ssid"
passw = "passw"

brightness = 50 # 50%
debug = True

# -- [ pre-define ] --
max_udp_buffer_size = (255 * 3) + 2 # max buffer set by RGB.NET client
udp__buffer_size = 0

udp_port = 1872
tcp_port = 80

unbound = False # find a better way

endpoints = {}
channels = [ # serves as a reference to config
	[machine.Pin(0), 37], # change board.GP6 to board.D8 for a pi other than a pico
	[machine.Pin(5), 0],
	[machine.Pin(6), 0],
	[machine.Pin(8), 0]
]
pixels = [] # the actual controller
for i in range(len(channels)): 
	if channels[i][1] > 0: 
		pixels.insert(i, NeoPixel(channels[i][0], channels[i][1]))
		#pixels.fill((0, 0, 255))
		#pixels.write()

# -- [ core functions ] --
def connectWLAN():
	try:
		wlan = network.WLAN(network.STA_IF)
		wlan.active(True)
		wlan.connect(ssid, passw)
		return str(wlan.ifconfig()[0])
	except Exception as e:
		print("errored", e)
		machine.reset()

def createSock(host, port, timeout = 0.3, udp = False):
	# lower timeout = better. TCP timeout is causing missed packets for UDP
	# figure out how to properly make that asynchronous
	#
	# asyncio httpserver _may_ be the answer if i can figure out how to poll udp properly
	sock = socket.socket(socket.AF_INET, (udp == False and socket.SOCK_STREAM or socket.SOCK_DGRAM))
	sock.settimeout(timeout)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((host_ip, port))
	if udp == False:
		sock.listen(2)
		print(f"Listening at {host_ip}:{tcp_port}")
	else:
		print(f"UDP bound to {host_ip}:{udp_port}")
	
	return sock

async def main(host_ip):
	global brightness
	global udp_buffer_size
	brightness /= 100
	udp_buffer_size = (trueMax(channels) * 3) + 2 # more respectful of resources.  (num_leds * RGB) + headers
	
	if udp_buffer_size > max_udp_buffer_size:
		print(f"Too many LEDs: {(max_udp_size - 2) / 3} / {(udp_size - 2) / 3}")
		machine.reset()
	
	tcp = createSock(host_ip, tcp_port)
	udp = createSock(host_ip, udp_port, udp = True)
	
	while True: # unfortunately this is still synchronous :(
		await asyncio.gather(
			asyncio.create_task(readTCP(tcp)),
			asyncio.create_task(readUDP(udp))
		)
		
async def readTCP(sock):
	client, addr = None, None
	try:
		client, addr = sock.accept()
	except OSError as e: # suppress
		pass
	finally:
		if client:
			req = client.recv(4096)
			req = str(req, "utf-8").split()
			
			print(f"{addr} requested {req[1]}")
			endpoint = findEndpoint(req[1])
			
			client.send("HTTP/1.0 200 OK\r\n\r\n" + endpoint(req[len(req) - 1]))
			client.close()

async def readUDP(sock):
	data, addr = None, None
	if unbound == False:
		try:
			data, addr = sock.recvfrom(udp_buffer_size)
		except OSError as e: # suppress
			pass
		finally:
			if data:
				#print(f"Received UDP from {addr}") # for debugging
				seq, channel, bytes = data[0], data[1] - 1, list(data[2:udp_buffer_size])

				for i in range(channels[channel][1]): # not writing maybe my wiring is wrong
					pixels[channel][i] = (
						int(bytes[(i * 3)] * brightness),     # R index / brightness
						int(bytes[(i * 3) + 1] * brightness), # G index / brightness
						int(bytes[(i * 3) + 2] * brightness)  # B index / brightness
					)
				
				pixels[channel].write()
			
def findEndpoint(endpoint):
	if endpoint in endpoints: # this has failed before??
		return endpoints[endpoint]

def trueMax(t):
	last = 0
	for i in range(len(t)):
		if t[i][1] > last:
			last = t[i][1]
			
	return last

# -- [ artemis endpoints ] --
def serveRoot(body):
	return f'''
		<html>
			<head>
				<title>About PixelPusher</title>
			</head>
			<body>
				<h1>PixelPusher </h1>
				This device is currently running MicroPython on a Pi Pico W!<br/>
				<br/>
				Check <a href="https://github.com/ProtectiveManEgg/PixelPusher">PixelPusher</a> for more info on this project!<br/>
				Special thanks to <a href=\"https://github.com/DarthAffe/RGB.NET\">RGB.NET</a>! I based this project upon their NodeMCU Sketch!<br/>
				<br/>
				<h3>Configuration:</h3>
				<b>UDP:</b> "{unbound == False and "enabled (" + str(udp_port) + ")" or "disabled"}"<br/>
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
	'''
endpoints["/"] = serveRoot

def serveConfig(body):
	config = [
		{"channel": 1, "leds": channels[0][1]},
		{"channel": 2, "leds": channels[1][1]},
		{"channel": 3, "leds": channels[2][1]},
		{"channel": 4, "leds": channels[3][1]}
	]
	return json.dumps(config)
endpoints["/config"] = serveConfig

def serveReset(body):
	for i in range(len(pixels)):
		pixels[i].fill((0, 0, 0))
		pixels[i].write() # show?
	
	return ""
endpoints["/reset"] = serveReset

def serveUpdate(body):
	# same as udp but over http i think
	
	return ""
endpoints["/update"] = serveUpdate

def enableUDP(body):
	global unbound
	
	#udp_port = int(body) # need it bound sooner. using static value. look into this
	unbound = False
	
	return ""
endpoints["/enableUDP"] = enableUDP

def disableUDP(body):
	global unbound
	unbound = True
	
	return ""
endpoints["/disableUDP"] = disableUDP

# -- [[ my endpoints ]]
def serveConsole(body):
	f = open("./sd/console.html", "r")
	d = f.read()
	f.close()
	
	return d
endpoints["/console"] = serveConsole

if __name__ == "__main__":
	host_ip = connectWLAN()
	if host_ip is not None:
		print("Successfully connectected to WIFI")
		asyncio.run(main(host_ip))

