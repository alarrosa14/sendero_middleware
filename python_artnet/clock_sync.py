import socket
import math
import time
import sys

# UDP_IP = "255.255.255.255"
# IPS = ["192.168.1.128", "192.168.1.122", "192.168.1.148"]
#IPS = ["192.168.1.148", "192.168.1.129"]
# IPS = ["192.168.43.152", "192.168.43.32", "192.168.43.191"]

UDP_SEND_PORT = 8888
UDP_RECV_PORT = 8889

def send(stri, IPS, sock):
	for ip in IPS:
		sock.sendto(stri, (ip, UDP_SEND_PORT))	

initial_millis = int(round(time.time() * 1000))
millis = lambda: int(round(time.time() * 1000)) - initial_millis

def synchronize_clocks(IPS):
	sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	d = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	send("clock_request", IPS, sock_send)
	print("Clock request sent.")
	print("Waiting for response...")

	sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_recv.bind(("0.0.0.0",UDP_RECV_PORT))
	sock_recv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	device_millis = []
	device_millis_avg = 0.0
	for ip in IPS:
		data, addr = sock_recv.recvfrom(100)
		device_millis.append(long(data))
		device_millis_avg += long(data)

	device_millis_avg = device_millis_avg / len(IPS)
	
	current_millis = millis()

	print("Current millis:")
	print(current_millis)

	for idx  in range(len(IPS)):
		offset = current_millis - device_millis[idx]
		sock_send.sendto("adjust_clock " + str(offset), (IPS[idx], UDP_SEND_PORT))

# sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock_recv.bind(("0.0.0.0",UDP_RECV_PORT))
# sock_recv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# initial_millis = long(round(time.time() * 1000))
# millis = lambda: long(round(time.time() * 1000)) - initial_millis


# while True:
# 	send("clock_request")
# 	print("Clock request sent.")
# 	print("Waiting for response...")

# 	device_millis = []
# 	device_millis_avg = 0.0
# 	for ip in IPS:
# 		data, addr = sock_recv.recvfrom(100)
# 		device_millis.append(long(data))
# 		device_millis_avg += long(data)

# 	device_millis_avg = device_millis_avg / len(IPS)
	
# 	current_millis = millis()

# 	print("Current millis:")
# 	print(current_millis)

# 	for idx  in range(len(IPS)):
# 		offset = current_millis - device_millis[idx]
# 		sock_send.sendto("adjust_clock " + str(offset), (IPS[idx], UDP_SEND_PORT))

# 	time.sleep(3)



