import struct

from device_manager import millis
import device_manager.DeviceManager

REQUEST_CLOCK = 1
CLOCK_CORRECTION_OFFSET = 2
CONFIGURATION = 4
IS_RESPONSE = 128

class Device:

	def __init__(self, device_id, connection_socket, active=False):
		self.id = device_id
		self.connection_socket = connection_socket
		self.active = active

	def __str__(self):
		return "< active={0}, id={1}, raddr={2} >".format(
			self.active, self.id, self.connection_socket.getpeername())

	def request_clock(self):
		self.send_control_packet(True, False, False)

	def send_control_packet(self, request_clock=False, clock_correction_offset=False, configuration=False, data=b''):
		word_to_send = 0
		word_to_send = (word_to_send | REQUEST_CLOCK) if request_clock else word_to_send
		word_to_send = (word_to_send | CLOCK_CORRECTION_OFFSET) if clock_correction_offset else word_to_send
		word_to_send = (word_to_send | CONFIGURATION) if configuration else word_to_send
		
		self.connection_socket.send(struct.pack('7sB{0}s'.format(len(data)), b'SENDERO', word_to_send, data))

	def send_clock_correction_offset(self, offset=0):
		self.send_control_packet(False, True, False, struct.pack('i', offset))

	def synchronize_device_clock(self):
		rtt = millis()
		self.request_clock()
		sendero_header = self.connection_socket.recv(8)
		print("el header")
		print(sendero_header)
		if len(sendero_header) == 8:
			print("largo 8!")
			(s_header, s_mask) = struct.unpack('7sB', sendero_header)
			print(s_header)
			print(s_mask)
			if s_header == b'SENDERO' and s_mask == REQUEST_CLOCK | IS_RESPONSE:
				device_time = struct.unpack('i', self.connection_socket.recv(4))[0]
				current_millis = millis()
				rtt = current_millis - rtt
				offset = int((current_millis - device_time) + (rtt/2.0))
				print("offset: {3} , rtt: {2} -> device {0} vs {1} server".format(int(device_time + (rtt/2)), current_millis, rtt, offset))
				self.send_clock_correction_offset(offset)
