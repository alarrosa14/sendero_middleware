import sys
import socket
import math
import time

import struct

from python_artnet import clock_sync

def list_to_string(list):
	result = "";
	for elem in list:
		result += chr(elem)
	return result


def send_dancing_sins(UDP_IP, UDP_PORT):
	time.sleep(10)
	print(("Sending dancing sins to {0}:{1}...").format(
        UDP_IP, UDP_PORT))

	message = [0]*24

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	
	t = 0
	scale = 0
	seq = 0


	while True:

		# raw_input()
		r = int(255*(math.sin(t) + 1)/2)
		g = int(255*(math.sin(t+3) + 1)/2)
		b = int(255*(math.sin(t+4) + 1)/2)
		color = [r,g,b]

		for i in range(0,24,3):
			message[i:i+3] = color

		packet = struct.pack("<iH24B", int(clock_sync.millis() + 200), seq, *message)

		sock.sendto(packet, (UDP_IP, UDP_PORT))
		
		seq += 1
		t += 0.042
		time.sleep(0.042)

		if seq % 100 == 0:
			print("Current sequence number/time: {0} - {1}".format(seq, clock_sync.millis()))
			#if seq % 200 == 0:
			#	clock_sync.synchronize_clocks(IPS)

		# if clock_sync.millis() >= 300000:
		# 	break

