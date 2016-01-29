import sys
import socket
import math
import time
import conf

import struct

from python_artnet import clock_sync


def list_to_string(list):
    result = ""
    for elem in list:
        result += chr(elem)
    return result


def send_dancing_sins(UDP_IP, UDP_PORT):
    # time.sleep(5)
    print(("Sending dancing sins to {0}:{1} for {2} pixels...").format(
        UDP_IP, UDP_PORT, conf.GLOBAL_PIXELS_QTY))

    message = [0] * 3 * conf.GLOBAL_PIXELS_QTY

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    t = 0
    scale = 0
    seq = 0

    while True:
        # input()
        r = int(255 * (math.sin(t) + 1) / 2)
        g = int(255 * (math.sin(t + 3) + 1) / 2)
        b = int(255 * (math.sin(t + 4) + 1) / 2)
        color = [r, g, b]

        for i in range(0, 3 * conf.GLOBAL_PIXELS_QTY, 3):
            message[i:i + 3] = color

        packet = struct.pack("<iH{0}B".format(3 * conf.GLOBAL_PIXELS_QTY), int(clock_sync.millis() + 200), seq, *message)

        print(packet)
        sock.sendto(packet, (UDP_IP, UDP_PORT))

        seq += 1
        t += 0.042
        time.sleep(0.042)

        if seq % 100 == 0:
            print("Current sequence number/time: {0} - {1}".format(seq, clock_sync.millis()))
