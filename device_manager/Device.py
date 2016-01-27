import struct
import conf

from device_manager import millis
import device_manager.DeviceManager

REQUEST_CLOCK = 1
CLOCK_CORRECTION_OFFSET = 2
CONFIGURATION = 4
CLOSE_CONNECTION = 8
REQUEST_STATS = 16


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

        # Send initial packet:
        if device_id in conf.DEVICE_CONFIG:
            device_config = conf.DEVICE_CONFIG[device_id]
            initial_packet_payload = ""
            for key, value in device_config.items():
                initial_packet_payload += "{0}:{1} ".format(key, value)

            initial_packet_payload += "{0}:{1}\0".format(
                "Global.pixelsQty", conf.GLOBAL_PIXELS_QTY)

            rtt = millis()
            self.send_control_packet(True, False, True, False, False, bytes(initial_packet_payload, encoding="ASCII"))
            self.synchronize_device_clock(rtt)


    def __del__(self):
        if self.connection_socket:
            self.connection_socket.close()

    def __str__(self):
        return "< active={0}, id={1}, raddr={2} >".format(
            self.active, self.id, self.connection_socket.getpeername())

    def request_clock(self):
        self.send_control_packet(True, False, False)

    def send_control_packet(self, request_clock=False, clock_correction_offset=False, configuration=False, close_connection=False, request_stats=False, data=b''):
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
        print(struct.pack('7sB{0}s'.format(len(data)), b'SENDERO', word_to_send, data))

        if not connection_established:                
            try:
                self.connection_socket.connect((self.raddr[0], conf.DeviceManager.CONNECTION_PORT))
            except Exception as e:
                print("Something's wrong with %s. Exception type is %s" % (addr[0], e))
                self.connection_socket.close()

        self.connection_socket.send(
            struct.pack('7sB{0}s'.format(len(data)), b'SENDERO', word_to_send, data))

        self.connection_established = not close_connection

    def send_clock_correction_offset(self, offset=0):
        self.send_control_packet(False, True, False, True, False, struct.pack('i', offset))

    def synchronize_device_clock(self, rtt):
        # rtt = millis()
        # self.request_clock()
        sendero_header = self.connection_socket.recv(8)
        print("el header")
        print(sendero_header)
        if len(sendero_header) == 8:
            print("largo 8!")
            (s_header, s_mask) = struct.unpack('7sB', sendero_header)
            print(s_header)
            print(s_mask)
            if s_header == b'SENDERO':
                device_time = struct.unpack(
                    'i', self.connection_socket.recv(4))[0]
                current_millis = millis()
                rtt = current_millis - rtt
                offset = int((current_millis - device_time) + (rtt/2.0))
                print("offset: {3} , rtt: {2} -> device {0} vs {1} server".format(
                    int(device_time + (rtt/2)), current_millis, rtt, offset))
                self.send_clock_correction_offset(offset)
            else:
                print("Packet header was not SENDERO")

    def request_stats(self):
        self.send_control_packet(False, False, False, False, True, b'')
        sendero_header = self.connection_socket.recv(8)
        if len(sendero_header) == 8:
            (s_header, s_mask) = struct.unpack('7sB', sendero_header)
            if s_header == b'SENDERO':
                recv_aux = self.connection_socket.recv(1)
                stats_string = str(recv_aux) 
                while recv_aux != '\0':
                    recv_aux = self.connection_socket.recv(1)
                    if recv_aux != '\0':
                        stats_string += str(recv_aux)
                stats = dict([stat.split(':') for stat in stats_string.split()])
                print(stats)
