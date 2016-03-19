#!/usr/bin/python

import sys

from sendero_middleware import devices, streaming, config

"""
Sendero Middleware

It's a middleware between an ArtNet Server (like Sendero Server) and the Sendero-Wireless-Module.
In addition to translating ArtNet to Sendero-Wireless-Protocol, this middleware is responsible for the device management,
the control server and a set of streaming tests.

It offers the following execution modes:

- sin:          Streams a sin-controlled lighting pattern in broadcast mode.
                Accepts the streaming port as a parameter.

- artnet:       Receives, adapts and redirects ArtNet packets in broadcast mode.

- devserver:    Starts a straming session with device management.
                Allows an extra parameter to send a simulated streaming.

- prodserver:   Starts a streaming session with device management, control and keep-alive servers.
                Allows an extra parameter to send a simulated streaming.

Invocation call:
python3 middleware.py <execution mode> [extra params]
"""

if (len(sys.argv) > 1):
    # ##########################################################################################################
    # Sin Mode
    # ##########################################################################################################
    if (sys.argv[1] == "sin"):
        if len(sys.argv) > 2:
            streaming.send_dancing_sins(config.BROADCAST_IP, int(sys.argv[2]))
        else:
            streaming.send_dancing_sins(config.BROADCAST_IP, config.BROADCAST_PORT)

    # ##########################################################################################################
    # ArtNet Mode
    # ##########################################################################################################
    if (sys.argv[1] == "artnet"):
        devices.listen_for_devices()
        streaming.listen_and_redirect_artnet_packets(config.UDP_IP, config.UDP_PORT, config.BROADCAST_PORT)

    # ##########################################################################################################
    # Dev-Server Mode
    # ##########################################################################################################
    if (sys.argv[1] == "devserver"):
        devices.listen_for_devices()
        if len(sys.argv) > 2 and sys.argv[2] == "sin":
            streaming.send_dancing_sins()
        if len(sys.argv) > 2 and sys.argv[2] == "flash":
            streaming.send_flashing_lights()
        if len(sys.argv) > 2 and sys.argv[2] == "artnet":
            streaming.listen_and_redirect_artnet_packets(config.UDP_IP, config.UDP_PORT, config.STREAMING_DST_PORT)

    # ##########################################################################################################
    # Prod-Server Mode
    # ##########################################################################################################
    if (sys.argv[1] == "prodserver"):
        devices.listen_for_devices()
        devices.start_control_server()
        devices.start_sending_keep_alive()
        streaming.listen_and_redirect_artnet_packets(config.UDP_IP, config.UDP_PORT, config.BROADCAST_PORT)

else:
    print("Options:")
    print("\tmiddleware sin         >   sends the dancing sins")
    print("\tmiddleware artnet      >   starts the artnet middleware")
    print("\tmiddleware devserver   >   starts the device server")
    print("\tmiddleware prodserver  >   starts the production server")

while True:
    try:
        pass
    except KeyboardInterrupt:
        sys.exit(0)
