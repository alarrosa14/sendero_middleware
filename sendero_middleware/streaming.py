import sys

from socket import (socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR,
                    SO_BROADCAST)

import struct
import math
import time

from sendero_middleware import config, devices

####
# Artnet:

ARTNET_HEADER = b'Art-Net\x00'


def unpack_raw_artnet_packet(raw_data):

    if struct.unpack('!8s', raw_data[:8])[0] != ARTNET_HEADER:
        print("Received a non Art-Net packet")
        return None

    packet = {}
    (packet.op_code, packet.ver, packet.sequence, packet.physical,
        packet.universe, packet.length) = struct.unpack(
        '!HHBBHH', raw_data[8:18])

    packet.data = struct.unpack(
        '{0}s'.format(int(packet.length)),
        raw_data[18:18 + int(packet.length)])[0]

    return packet


def listen_and_redirect_artnet_packets(udp_ip, udp_port, broadcast_port):
    print(("Listening in {0}:{1} and redirecting with "
           "destination port {2}...").format(
        udp_ip, udp_port, broadcast_port))

    sock = socket(AF_INET, SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    sock_broadcast = socket(AF_INET, SOCK_DGRAM)
    sock_broadcast.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock_broadcast.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            packet = unpack_raw_artnet_packet(data)
            sock_broadcast.sendto(
                packet.data[:24], ('255.255.255.255', broadcast_port))
        except KeyboardInterrupt:
            sock.close()
            sock_broadcast.close()
            sys.exit()

####


####
# Sins:

def send_dancing_sins(udp_ip, udp_port):
    # time.sleep(5)
    print(("Sending dancing sins to {0}:{1} for {2} pixels...").format(
        udp_ip, udp_port, config.GLOBAL_PIXELS_QTY))

    message = [0] * 3 * config.GLOBAL_PIXELS_QTY

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    t = 0
    seq = 0

    # Wait for connections
    while not (devices.device_connected_qty() == 3):
        time.sleep(1)
        print('**** Waiting for connections ***')
        pass

    while True:

        # raw_input()
        r = int(255 * (math.sin(t) + 1) / 2)
        g = int(255 * (math.sin(t + 3) + 1) / 2)
        b = int(255 * (math.sin(t + 4) + 1) / 2)
        color = [r, g, b]

        for i in range(0, 3 * config.GLOBAL_PIXELS_QTY, 3):
            # Black and red
            if seq % 2 == 0:
                message[i:i + 3] = [0, 0, 0]
            else:
                message[i:i + 3] = [0, 255, 0]
            # message[i:i + 3] = color

        packet = struct.pack("<iH{0}B".format(3 * config.GLOBAL_PIXELS_QTY),
                             int(devices.millis() + 200), seq, *message)

        sock.sendto(packet, (udp_ip, udp_port))

        seq += 1
        # t += 0.042
        t += 5
        time.sleep(0.042)

        if seq % 100 == 0:
            print(
                "Current sequence number/time: "
                "{0} - {1}".format(seq, devices.millis()))

        if seq == 1000:
            devices.request_statistics()
            sys.exit(0)

####
