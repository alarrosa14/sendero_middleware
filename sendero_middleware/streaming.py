"""Sendero Streaming module."""

import struct
import sys

from socket import (
    socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST)

import math
import time

from sendero_middleware import config, utils

SYNC_EXPIRATION = 1

clock_expiration_period_finish = None


def notify_sync_expiration():
    """
    Notify about new device.

    This must be called only when config.ENABLE_CLOCK_EXPIRATION_FLAG
    is enabled.
    Will make the streaming send SYNC_EXPIRATION flag to the devices
    for config.CLOCK_EXPIRATION_PERIOD milliseconds.
    """
    global clock_expiration_period_finish
    assert(config.ENABLE_CLOCK_EXPIRATION_FLAG)
    clock_expiration_period_finish = \
        utils.millis() + config.CLOCK_EXPIRATION_PERIOD


def listen_and_redirect_artnet_packets(udp_ip, udp_port, broadcast_port):
    """
    Art-Net packet listener.

    Receive ArtNet data from udp_ip:udp_port, translates to
    Sendero-Wireless-Protocol and redirects to broadcast_ip:broadcast_port.
    """
    print(("Listening in {0}:{1} and redirecting to " + config.BROADCAST_IP +
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
            data, addr = sock_artnet.recvfrom(config.ARTNET_MAX_PACKAGE_LEN)

            # Upack the ArtNet data
            message = utils.unpack_raw_artnet_packet(data)

            # Generate the flags
            flags = 0
            if config.ENABLE_CLOCK_EXPIRATION_FLAG:
                if (clock_expiration_period_finish and
                        time.millis() < clock_expiration_period_finish):
                    flags = flags | SYNC_EXPIRATION
                else:
                    clock_expiration_period_finish = None

            # Construct the Sendero-Data-Packet
            packet = utils.sendero_data_packet(
                message['sequence'], flags, message['data'])

            # Send to broadcast address
            sock_broadcast.sendto(
                packet, (config.BROADCAST_IP, broadcast_port))

            if int(message['sequence']) % 128 == 0:
                print(
                    "ArtNet - Current sequence number/time: "
                    "{0} - {1}".format(message['sequence'], utils.millis()))

        except KeyboardInterrupt:
            sock_artnet.close()
            sock_broadcast.close()
            sys.exit()


def send_dancing_sins(udp_ip, udp_port):
    """Stream the dancing sins to udp_ip:udp_port."""
    print(("Sending dancing sins to {0}:{1} for {2} pixels...").format(
        udp_ip, udp_port, config.GLOBAL_PIXELS_QTY))

    message = [0] * 3 * config.GLOBAL_PIXELS_QTY

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    t = 0
    seq = 0

    global clock_expiration_period_finish

    while True:

        # Uncomment the line below to send a package on each key press
        # input()
        r = int(255 * (math.sin(t) + 1) / 2)
        g = int(255 * (math.sin(t + 3) + 1) / 2)
        b = int(255 * (math.sin(t + 4) + 1) / 2)
        color = [r, g, b]

        for i in range(0, 3 * config.GLOBAL_PIXELS_QTY, 3):
            message[i:i + 3] = color

        flags = 0
        if config.ENABLE_CLOCK_EXPIRATION_FLAG:
            if (clock_expiration_period_finish and
                    utils.millis() < clock_expiration_period_finish):
                flags = flags | SYNC_EXPIRATION
            else:
                clock_expiration_period_finish = None

        packet = utils.sendero_data_packet(seq, flags, message)


        # print(struct.unpack("<iBB{0}B".format(3 * config.GLOBAL_PIXELS_QTY), packet)[2])

        sock.sendto(packet, (udp_ip, udp_port))

        seq = utils.increment_seq(seq)
        t += 0.04167
        time.sleep(0.04167)

        if seq % 128 == 0:
            print(
                "Sin - Current sequence number/time: "
                "{0} - {1}".format(seq, utils.millis()))
