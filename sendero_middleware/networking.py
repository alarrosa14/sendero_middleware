import socket
from sendero_middleware import config
from socket import (
	socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP)

if config.MULTICAST_ENABLED:
	sock = socket(AF_INET, SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)
else:
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def send_streaming_packet(packet):
	sock.sendto(packet, (config.STREAMING_DST_IP, config.STREAMING_DST_PORT))
