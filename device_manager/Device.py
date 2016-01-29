import struct
import conf
import socket

from device_manager import millis

REQUEST_CLOCK = 1
CLOCK_CORRECTION_OFFSET = 2
CONFIGURATION = 4
CLOSE_CONNECTION = 8
REQUEST_STATS = 16
KEEP_ALIVE = 32


class Device:

    def __init__(self, device_id, connection_socket, active=False):
        if type(device_id) != int:
            raise "Incorrect device id: {0}".format(device_id)
        print("Creating device with id " + str(device_id))

        self.id = device_id
        self.connection_socket = connection_socket
        self.active = active
        self.connection_established = True
        self.raddr = self.connection_socket.getpeername()

        server_clock_before_send = millis()
        self.set_initial_configs()
        self.synchronize_device_clock(server_clock_before_send)

    def __del__(self):
        if self.connection_socket:
            self.connection_socket.close()

    def __str__(self):
        return "< active={0}, id={1}, raddr={2} >".format(
            self.active, self.id, self.raddr)

    ##########################################################################################
    # Commands
    ##########################################################################################

    def set_initial_configs(self):
        # Send initial packet
        initial_packet_payload = ""

        # Device configs
        for key, value in conf.DEVICE_CONFIG[self.id].items():
            initial_packet_payload += "{0}:{1} ".format(key, value)

        # Global configs
        for key, value in conf.GLOBAL_CONFIG.items():
            initial_packet_payload += "{0}:{1} ".format(key, value)
        initial_packet_payload += "\0"

        self.send_control_packet(True, False, True, False, False, False, bytes(initial_packet_payload, encoding="ASCII"))

    def request_clock(self):
        self.send_control_packet(True, False, False)

    def send_clock_correction_offset(self, offset=0):
        self.send_control_packet(False, True, False, True, False, False, struct.pack('i', offset))

    def synchronize_device_clock(self, server_clock_before_send):
        sendero_header = self.connection_socket.recv(8)
        print(sendero_header)
        if len(sendero_header) == 8:
            (s_header, s_mask) = struct.unpack('7sB', sendero_header)
            print(s_header)
            print(s_mask)
            if s_header == b'SENDERO':
                device_time = struct.unpack(
                    'i', self.connection_socket.recv(4))[0]
                current_millis = millis()
                rtt = current_millis - server_clock_before_send
                offset = int((current_millis - device_time) + (rtt / 2.0))
                print("offset: {3} , rtt: {2} -> device {0} vs {1} server".format(
                    int(device_time + (rtt / 2)), current_millis, rtt, offset))
                self.send_clock_correction_offset(offset)
            else:
                print("Packet header was not SENDERO")

    def request_stats(self):
        self.send_control_packet(False, False, False, False, True, False, b'')
        sendero_header = self.connection_socket.recv(8)
        if len(sendero_header) == 8:
            (s_header, s_mask) = struct.unpack('7sB', sendero_header)
            if s_header == b'SENDERO':

                self.connection_socket.settimeout(30)
                recv_aux = self.connection_socket.recv(1)
                self.connection_socket.settimeout(None)

                stats_string = recv_aux.decode("ASCII")
                while recv_aux != b'\0':
                    self.connection_socket.settimeout(30)
                    recv_aux = self.connection_socket.recv(1)
                    self.connection_socket.settimeout(None)

                    if recv_aux != b'\0':
                        stats_string += recv_aux.decode("ASCII")

                stats = dict([stat.split(':') for stat in stats_string.split()])
                print(stats)

    def send_keep_alive(self):
        self.send_control_packet(False, False, False, False, False, True)

    ##########################################################################################
    # Packet Builder
    ##########################################################################################

    def send_control_packet(self, request_clock=False, clock_correction_offset=False, configuration=False, close_connection=False, request_stats=False, keep_alive=False, data=b''):
        word_to_send = 0
        word_to_send = (
            word_to_send | REQUEST_CLOCK) if request_clock else word_to_send
        word_to_send = (
            word_to_send | CLOCK_CORRECTION_OFFSET) if clock_correction_offset else word_to_send
        word_to_send = (
            word_to_send | CONFIGURATION) if configuration else word_to_send
        word_to_send = (
            word_to_send | CLOSE_CONNECTION) if close_connection else word_to_send
        word_to_send = (
            word_to_send | REQUEST_STATS) if request_stats else word_to_send
        word_to_send = (
            word_to_send | KEEP_ALIVE) if keep_alive else word_to_send
        print(struct.pack('7sB{0}s'.format(len(data)), b'SENDERO', word_to_send, data))

        if not self.connection_established:
            # Try to reconnect
            try:
                self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection_socket.connect((self.raddr[0], conf.DeviceManager.CONNECTION_PORT))
            except Exception as e:
                print("Something's wrong with %s. Exception type is %s" % (self.raddr[0], e))
                self.connection_socket.close()
                raise

        self.connection_socket.send(
            struct.pack('7sB{0}s'.format(len(data)), b'SENDERO', word_to_send, data))

        self.connection_established = not close_connection

        if close_connection:
            self.connection_socket.close()
