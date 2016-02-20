# Sendero Middleware #

#### < Work in progress ... >

## Introduction

It's a middleware between an ArtNet Server (like Sendero Server) and the [Sendero-Wireless-Module](https://github.com/dernster/WirelessBondibar).

In addition to translating [ArtNet](http://art-net.org.uk/) to Sendero-Wireless-Protocol, this middleware is responsible for the device management,
the control server and a set of streaming tests.

It offers the following execution modes:

- sin:          Streams a sin-controlled lighting pattern in broadcast mode.
                Accepts the streaming port as a parameter.

- artnet:       Receives, adapts and redirects ArtNet packets in broadcast mode.

- devserver:    Starts a straming session with device management.
                Allows an extra parameter to send a simulated streaming.

- prodserver:   Starts a streaming session with device management, control and keep-alive servers.
                Allows an extra parameter to send a simulated streaming.
                
## Modules

- config: Stores all the configurable settings.

- streaming: Module responsible of the translation and redirection of Art-Net packets.

- utils: A set of utilitary methods for the whole app.

- devices: Device manager, is responsible for all the actions related to a wireless device. 
(Registering, Controlling, etc...)

## Settings

- ARTNET_HEADER = 'Art-Net\x00'
- ARTNET_MAX_PACKAGE_LEN = 1024
- BROADCAST_IP = '255.255.255.255'
- BROADCAST_PORT = 7788
- CONNECTION_PORT = 8889
- DEFAULT_DEVICE_MANAGED_PIXELS_QTY = 8
- DEVICE_CONFIG = {1: {'Device.firstPixel': 0, 'Device.managedPixelsQty'...
- GLOBAL_CONFIG = {'ControlServer.keepAliveSeconds': 20, 'Global.pixelsQ...
- GLOBAL_PIXELS_QTY = 91
- KEEP_ALIVE_INTERVAL = 10
- PLAYBACK_TIME_DELAY = 200
- REGISTRATION_PORT = 8888
- SEQ_MAX = 255
- STATS_REQUEST_INTERVAL = 3600
- UDP_IP = '0.0.0.0'
- UDP_PORT = 7777

## Invocation 

python3 middleware.py < execution mode > [extra params]
