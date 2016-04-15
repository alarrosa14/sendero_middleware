"""Sendero Streaming module."""

import sys

from socket import (
    socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST)

import math
import time
from sendero_middleware import config, utils, networking

SYNC_EXPIRATION = 1

clock_expiration_period_finish = None

"""
This sets the maximum length for the received ArtNet packages.
"""
ARTNET_MAX_PACKAGE_LEN = 1024


def listen_and_redirect_artnet_packets(udp_ip, udp_port, broadcast_port):
    """
    Art-Net packet listener.

    Receive ArtNet data from udp_ip:udp_port, translates to
    Sendero-Wireless-Protocol and redirects to broadcast_ip:broadcast_port.
    """
    print(("Listening in {0}:{1} and redirecting to " + "multicast_group" +
           ":{2}...").format(udp_ip, udp_port, broadcast_port))

    # Socket to receive from Sendero Server
    sock_artnet = socket(AF_INET, SOCK_DGRAM)
    sock_artnet.bind((udp_ip, udp_port))

    # Socket to redirect ArtNet data
    sock_broadcast = socket(AF_INET, SOCK_DGRAM)
    sock_broadcast.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock_broadcast.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    global clock_expiration_period_finish

    while True:
        try:
            # Receive data from an ArtNet Server
            data, addr = sock_artnet.recvfrom(ARTNET_MAX_PACKAGE_LEN)

            # Upack the ArtNet data
            message = utils.unpack_raw_artnet_packet(data)

            # Generate the flags
            flags = 0

            # Construct the Sendero-Data-Packet
            networking.send_streaming_packet(
                message['sequence'], flags, message['data'])

            if int(message['sequence']) % 128 == 0:
                print(
                    "ArtNet - Current sequence number/time: "
                    "{0} - {1}".format(message['sequence'], utils.millis()))

        except KeyboardInterrupt:
            sock_artnet.close()
            sock_broadcast.close()
            sys.exit()


def send_dancing_sins():
    """Stream the dancing sins to udp_ip:udp_port."""
    print("Sending dancing sins...")

    message = [0] * 3 * config.GLOBAL_PIXELS_QTY

    t = 0
    seq = 0

    global clock_expiration_period_finish

    while True:

        # Uncomment the line below to send a package on each key press
        # input()
        r = int(255 * (math.sin(t * 4.12456654) + 1) / 2)
        g = 255 - int(255 * (math.sin(t * 5.313) + 1) / 2)
        b = int(255 * (math.sin(t * 9.125412) + 1) / 2)
        color = [r, g, b]

        for i in range(0, 3 * config.GLOBAL_PIXELS_QTY, 3):
            message[i:i + 3] = color

        flags = 0

        networking.send_streaming_packet(seq, flags, message)

        seq = utils.increment_seq(seq)
        t += config.FRAME_RATE
        time.sleep(config.FRAME_RATE)

        if seq % 128 == 0:
            print(
                "Sin - Current sequence number/time: "
                "{0} - {1}".format(seq, utils.millis()))


def send_flashing_lights():
    """Stream the dancing sins to udp_ip:udp_port."""
    print("Sending flashing lights...")

    message = [0] * 3 * config.GLOBAL_PIXELS_QTY

    t = 0
    seq = 0

    global clock_expiration_period_finish

    while True:

        # Uncomment the line below to send a package on each key press
        # input()

        for i in range(0, 3 * config.GLOBAL_PIXELS_QTY, 3):
            if (t < config.FRAMES_PER_SECOND):
                message[i:i + 3] = [255, 255, 255]
            else:
                message[i:i + 3] = [0, 0, 0]

        flags = 0

        networking.send_streaming_packet(seq, flags, message)

        seq = utils.increment_seq(seq)
        t = (t + 1) % (config.FRAMES_PER_SECOND * 2)
        time.sleep(config.FRAME_RATE)

        if seq % 128 == 0:
            print(
                "Sin - Current sequence number/time: "
                "{0} - {1}".format(seq, utils.millis()))
