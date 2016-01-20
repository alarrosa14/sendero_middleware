#!/usr/bin/python

import sys

from python_artnet import artnet_middleware, sin_stream
from device_manager.DeviceManager import DeviceManager

UDP_IP = "255.255.255.255"
UDP_PORT = 7788

BROADCAST_PORT = 7788

if (len(sys.argv) > 1):
    if (sys.argv[1] == "sin"):
        sin_stream.send_dancing_sins(UDP_IP, UDP_PORT)
    if (sys.argv[1] == "artnet"):
        artnet_middleware.listen_and_redirect_artnet_packets(UDP_IP, UDP_PORT, BROADCAST_PORT)
    if (sys.argv[1] == "devserver"):
        DeviceManager.listen_for_devices()
    if (sys.argv[1] == "ctrlserver"):
        DeviceManager.listen_for_devices()
        DeviceManager.start_control_server()
        if len(sys.argv) > 2 and sys.argv[2] == "test":
            sin_stream.send_dancing_sins(UDP_IP, UDP_PORT)

else:
    print("Options:")
    print("\tmiddleware sin         >   sends the dancing sins")
    print("\tmiddleware artnet      >   starts the artnet middleware")
    print("\tmiddleware devserver   >   starts the device server")

while True:
    try:
        pass
    except KeyboardInterrupt:
        DeviceManager.stop()

#sys.exit()
