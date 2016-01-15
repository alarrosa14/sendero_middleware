import socket

UDP_IP = "192.168.1.148"
UDP_PORT = 2390
MESSAGE = [200,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,0]

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", MESSAGE)

def list_to_string(list):
	result = "";
	for elem in list:
		result += chr(elem)
	return result

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(list_to_string(MESSAGE), (UDP_IP, UDP_PORT))
