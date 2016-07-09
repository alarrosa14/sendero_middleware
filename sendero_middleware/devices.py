import socket
import threading
import time
import struct

from sendero_middleware import config, utils, streaming, networking

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

        self.set_initial_configs()

    def __del__(self):
        if self.connection_socket:
            self.connection_socket.close()

    def __str__(self):
        return "< active={0}, id={1}, raddr={2} >".format(
            self.active, self.id, self.raddr)

    ###########################################################################
    # Commands
    ###########################################################################

    def set_initial_configs(self):
        # Send initial packet
        initial_packet_payload = ""

        # Device configs
        for key, value in config.DEVICE_CONFIG[self.id].items():
            initial_packet_payload += "{0}:{1} ".format(
                key, (",".join(value) if type(value) == list else value))

        # Global configs
        for key, value in config.GLOBAL_DEVICES_CONFIGS.items():
            initial_packet_payload += "{0}:{1} ".format(key, value)

        # Add Multicast Group IP for device
        multicast_ip = networking.get_multicast_ip_for_device(self.id)
        initial_packet_payload += "{0}:{1} ".format(config.DeviceKeys.MULTICAST_GROUP_IP, multicast_ip)
        print(multicast_ip)

        # Set first pixel of multicast group
        first_multicast_pixel = networking.get_multicast_first_pixel_for_device(self.id)
        initial_packet_payload += "{0}:{1} ".format(config.DeviceKeys.MULTICAST_GROUP_FIRST_PIXEL, first_multicast_pixel)

        # Set playback delay of multicast group
        playbackDelay = networking.get_playback_time_delay_for_device(self.id)
        print("=============================")
        print("Device -> " + str(self.id) + " delay = " + str(playbackDelay))
        print("=============================")

        initial_packet_payload += "{0}:{1} ".format(config.DeviceKeys.PLAYBACK_DELAY, playbackDelay)

        # Add Multicast Group Total Pixels for device
        pixels_qty = networking.get_multicast_pixels_qty_for_device(self.id)
        initial_packet_payload += "{0}:{1}".format(config.DeviceKeys.STREAMING_PIXELS_QTY, pixels_qty)
        print(pixels_qty)

        initial_packet_payload += "\0"

        print(initial_packet_payload)

        self.send_control_packet(True, False, True, True, False, False, bytes(
            initial_packet_payload, encoding="ASCII"))

    def request_clock(self):
        self.send_control_packet(True, False, False)

    def send_clock_correction_offset(self, offset=0):
        self.send_control_packet(
            False, True, False, True, False, False, struct.pack('I', offset))

    def synchronize_device_clock(self, server_clock_before_send):
        sendero_header = self.connection_socket.recv(8)
        if len(sendero_header) == 8:

            (s_header, s_mask) = struct.unpack('7sB', sendero_header)
            if s_header == b'SENDERO':
                device_time = struct.unpack(
                    'i', self.connection_socket.recv(4))[0]
                current_millis = utils.millis()
                rtt = current_millis - server_clock_before_send
                offset = int((current_millis - device_time) + (rtt / 2.0))
                print("offset: {3} , rtt: {2} -> device {0} vs {1} "
                      "server".format(int(device_time + (rtt / 2)),
                                      current_millis, rtt, offset))
                self.send_clock_correction_offset(offset)
            else:
                print("Packet header was not SENDERO")

    def request_stats(self):
        stats_are_dirty = True
        success_count = 0
        stats = dict()
        while stats_are_dirty and success_count < 3:
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

                    stats = dict(
                        [stat.split(':') for stat in stats_string.split()])
                    # print("### Statistics from {0} ###".format(self.id))
                    # print(stats)
                    # print("###########")
                    stats_are_dirty = stats['Stats.dirty'] == 'True'
                    if not stats_are_dirty:
                        success_count += 1

            time.sleep(0.5)
        return (self.id, stats)

    def send_keep_alive(self):
        self.send_control_packet(False, False, False, False, False, True)

    ###########################################################################
    # Packet Builder
    ###########################################################################

    def send_control_packet(self, request_clock=False,
                            clock_correction_offset=False, configuration=False,
                            close_connection=False, request_stats=False,
                            keep_alive=False, data=b''):
        word_to_send = 0
        word_to_send = (
            word_to_send | REQUEST_CLOCK) if request_clock else word_to_send
        word_to_send = (
            word_to_send | CLOCK_CORRECTION_OFFSET) \
            if clock_correction_offset else word_to_send
        word_to_send = (
            word_to_send | CONFIGURATION) \
            if configuration else word_to_send
        word_to_send = (
            word_to_send | CLOSE_CONNECTION) \
            if close_connection else word_to_send
        word_to_send = (
            word_to_send | REQUEST_STATS) \
            if request_stats else word_to_send
        word_to_send = (word_to_send | KEEP_ALIVE)\
            if keep_alive else word_to_send

        if not self.connection_established:
            # Try to reconnect
            try:
                self.connection_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.connection_socket.connect(
                    (self.raddr[0], config.CONNECTION_PORT))
            except Exception as e:
                print("Something's wrong with %s. Exception type is %s" % (
                    self.raddr[0], e))
                self.connection_socket.close()
                raise

        self.connection_socket.send(
            struct.pack('7sB{0}s'.format(
                len(data)), b'SENDERO', word_to_send, data))

        self.connection_established = not close_connection

        if close_connection:
            self.connection_socket.close()


devices_connected = {}
lock = threading.Lock()


def add_device(device_id, device):
    lock.acquire()
    devices_connected[device_id] = device
    lock.release()


def device_connected_qty():
    res = 0
    lock.acquire()
    res = len(devices_connected)
    lock.release()
    return res


worker_enabled = True

def device_server_worker():
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.bind((config.UDP_IP, config.REGISTRATION_PORT))
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def sip_key_value(x):
        values = x.split(b'=')
        return None if len(values) != 2 else (values[0].decode("utf-8"), values[1].decode("utf-8"))

    while worker_enabled:
        print("Listening for Device Registering UDP messages...")
        data, addr = sock_udp.recvfrom(100)
        sip_packet = dict(list(map(lambda x: sip_key_value(x), data.split(b'\n'))))
        print(sip_packet)

        wbb_number = int(sip_packet["o"][4:])
        print(wbb_number)
        if wbb_number != None:
            print("Device sending SIP message: {0} from IP/port: {1}/{2}".format(
                sip_packet, addr[0], addr[1]))
            device_id = wbb_number

            if config.is_allowed_device(device_id):
                lock.acquire()
                if device_id in devices_connected:
                    print("A device with identifier {0} is already "
                          "registered".format(device_id))
                    print("Reconnecting...")
                    device = devices_connected.pop(device_id, 0)
                    if device:
                        del device
                lock.release()

                print("Will connect to {0}:{1}".format(
                    addr[0], config.CONNECTION_PORT))
                sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    sock_tcp.connect((addr[0], config.CONNECTION_PORT))
                except Exception as e:
                    print("Something's wrong with %s. Exception type is %s" % (
                        addr[0], e))
                    sock_tcp.close()
                    continue

                device = Device(device_id=device_id,
                                connection_socket=sock_tcp, active=True)

                add_device(device_id, device)

                print("New device registered: {0}".format(device))

            else:
                print(device_id, "is not an allowed device.")

def control_server_worker():
    current_device_index = 0
    request_stats_interval = config.STATS_REQUEST_INTERVAL
    while True:
        time.sleep(request_stats_interval)

        if device_connected_qty() > 0:
            lock.acquire()
            device = list(devices_connected.values())[
                current_device_index]
            current_device_index = (
                current_device_index + 1) % len(devices_connected)
            lock.release()

            device.request_stats()


def keep_alive_worker():
    keep_alive_interval = config.KEEP_ALIVE_INTERVAL
    while True:
        time.sleep(keep_alive_interval)

        if device_connected_qty() > 0:
            lock.acquire()
            device = list(devices_connected.values())
            lock.release()

            for d in device:
                d.send_keep_alive()


def listen_for_devices():
    print("Starting Device Registering thread...")
    listening_thread = threading.Thread(target=device_server_worker)
    listening_thread.daemon = True
    listening_thread.start()


def start_control_server():
    print("Starting Control Server thread...")
    t = threading.Thread(target=control_server_worker)
    t.daemon = True
    t.start()


def start_sending_keep_alive():
    print("Starting Keep Alive thread...")
    t = threading.Thread(target=keep_alive_worker)
    t.daemon = True
    t.start()


def request_statistics():
    print("Requesting statistics...")
    print("============= CONFIGURATION ============= ")
    configs = config.get_sorted_list_from_dictionary({
        "config.FRAMES_PER_SECOND": config.FRAMES_PER_SECOND,
        "config.MULTICAST_GROUPS_QTY": config.MULTICAST_GROUPS_QTY,
        "config.DELAY_BETWEEN_MULTICAST_PACKETS": config.DELAY_BETWEEN_MULTICAST_PACKETS,
        "config.PLAYBACK_TIME_DELAY": config.PLAYBACK_TIME_DELAY,
        "config.GLOBAL_PIXELS_QTY": config.GLOBAL_PIXELS_QTY,
        "networking.sorted_multicast_group_data": networking.sorted_multicast_group_data,
    })
    for k,v in configs:
        print("{0}={1}".format(k,v))
    print("")

    first = True
    rev = list(devices_connected.values())
    for d in rev:
        stats = d.request_stats()
        orderedList = config.get_sorted_list_from_dictionary(stats[1])
        if first:
            for k,v in orderedList:
                print("{0}\t".format(k), end="")
            print("")   
            first = False

        for k,v in orderedList:
            print("{0}\t".format(v), end="")
        print("")
