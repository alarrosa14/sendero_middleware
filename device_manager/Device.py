import struct

REQUEST_CLOCK = 4
CLOCK_CORRECTION_OFFSET = 2
CONFIGURATION = 1

class Device:

	def __init__(self, device_id, connection_socket, active=False):
		self.id = device_id
		self.connection_socket = connection_socket
		self.active = active

	def __str__(self):
		return "< active={0}, id={1}, raddr={2} >".format(
			self.active, self.id, self.connection_socket.getpeername())

	def send_control_packet(self, request_clock=False, clock_correction_offset=0, configuration=False):
		word_to_send = 0
		word_to_send = (word_to_send | REQUEST_CLOCK) if request_clock else word_to_send
		word_to_send = (word_to_send | CLOCK_CORRECTION_OFFSET) if clock_correction_offset else word_to_send
		word_to_send = (word_to_send | CONFIGURATION) if configuration else word_to_send
		
		self.connection_socket.send(struct.pack('8sB', b'SENDERO ', word_to_send))
