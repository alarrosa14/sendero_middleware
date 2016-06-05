#!/usr/bin/python3

import sys

from sendero_middleware import devices, streaming, config, networking
import time

"""
Sendero Middleware

It's a middleware between an ArtNet Server (like Sendero Server) and the Sendero-Wireless-Module.
In addition to translating ArtNet to Sendero-Wireless-Protocol, this middleware is responsible for the device management,
the control server and a set of streaming tests.

It offers the following execution modes:

- devserver:    Starts a straming session with device management.
                Allows an extra parameter to send a simulated streaming among sin|flash|artnet.


- prodserver:   Starts a streaming session with device management, control and keep-alive servers.
                Allows an extra parameter to send a simulated streaming.

Streams:

- sin:          Streams a sin-controlled lighting pattern in broadcast mode.

- flash:        Streams a flash pattern in broadcast mode.

- artnet:       Receives, adapts and redirects ArtNet packets in broadcast mode.



Invocation call:
python3 middleware.py <execution mode> [extra params]
"""

if (len(sys.argv) > 1):

    # ##########################################################################################################
    # Dev-Server Mode
    # ##########################################################################################################
    if (sys.argv[1] == "devserver"):
        devices.listen_for_devices()
        if len(sys.argv) > 2 and sys.argv[2] == "sin":
            streaming.send_dancing_sins()
        if len(sys.argv) > 2 and sys.argv[2] == "flash":
            streaming.send_flashing_lights()
        if len(sys.argv) > 2 and sys.argv[2] == "rgb":
            streaming.send_rgb_lights()
        if len(sys.argv) > 2 and sys.argv[2] == "artnet":
            streaming.listen_and_redirect_artnet_packets(config.UDP_IP, config.UDP_PORT, config.STREAMING_DST_PORT)
        if len(sys.argv) > 2 and sys.argv[2] == "nostream":
            while True:
                q = input() 
                if q == "q":
                    break
            time.sleep(2)
            devices.worker_enabled = False
            devices.request_statistics()
            networking.sock.close()
            sys.exit()


    # ##########################################################################################################
    # Prod-Server Mode
    # ##########################################################################################################
    if (sys.argv[1] == "prodserver"):
        devices.listen_for_devices()
        devices.start_control_server()
        devices.start_sending_keep_alive()
        streaming.listen_and_redirect_artnet_packets(config.UDP_IP, config.UDP_PORT, config.STREAMING_DST_PORT)


print("Options:")
print("\tmiddleware devserver sin|flash|artnet  >   starts the device server")
print("\tmiddleware prodserver                  >   starts the production server")
