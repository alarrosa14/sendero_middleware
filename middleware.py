#!/usr/bin/python

import sys

from sendero_middleware import devices, streaming

UDP_IP = "255.255.255.255"
UDP_PORT = 7788

BROADCAST_PORT = 7788

if (len(sys.argv) > 1):
    if (sys.argv[1] == "sin"):
        streaming.send_dancing_sins(UDP_IP, UDP_PORT)
    if (sys.argv[1] == "artnet"):
        streaming.listen_and_redirect_artnet_packets(
            UDP_IP, UDP_PORT, BROADCAST_PORT)
    if (sys.argv[1] == "devserver"):
        devices.listen_for_devices()
        if len(sys.argv) > 2 and sys.argv[2] == "test":
            streaming.send_dancing_sins(UDP_IP, UDP_PORT)
    if (sys.argv[1] == "ctrlserver"):
        devices.listen_for_devices()
        # devices.start_control_server()
        # devices.start_sending_keep_alive()
        if len(sys.argv) > 2 and sys.argv[2] == "test":
            streaming.send_dancing_sins(UDP_IP, UDP_PORT)

else:
    print("Options:")
    print("\tmiddleware sin         >   sends the dancing sins")
    print("\tmiddleware artnet      >   starts the artnet middleware")
    print("\tmiddleware devserver   >   starts the device server")

while True:
    try:
        pass
    except KeyboardInterrupt:
        sys.exit(0)
