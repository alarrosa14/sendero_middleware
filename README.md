# Sendero Middleware #

## Introduction

It's a middleware (ẁritten in Python3) between an ArtNet Server (like Sendero Server) and the Sendero-Wireless-Module.
In addition to translating ArtNet to Sendero-Wireless-Protocol, this middleware is responsible for the device management,
the control server and a set of streaming tests.

It offers the following execution modes:

- `devserver`:    Starts a straming session with device management.
                  Allows an extra parameter to send a simulated streaming among sin|flash|artnet.


- `prodserver`:   Starts a streaming session with device management, control and keep-alive servers.
                  Allows an extra parameter to send a simulated streaming.

Stream modes:

- `sin`:          Streams a sin-controlled lighting pattern.

- `flash`:        Streams a flash pattern in broadcast mode.

- `artnet`:       Receives, adapts and redirects ArtNet packets.


                
## Modules

- `config`: Stores all the configurable settings.

- `streaming`: Module responsible of the translation and redirection of Art-Net packets.

- `utils`: A set of utilitary methods for the whole app.

- `devices`: Device manager, is responsible for all the actions related to a wireless device. 
(Registering, Controlling, etc...)

- `networking`: Used to manage multicast mode. The frame information can be sent in 2 modes: broadcast|multicast.
              In broadcast mode, UDP broadcast IP is used (255.255.255.255) and all frame data is sent in just 1 packet.
              For artworks containing a lot of pixels, the size of the packet can be divided using multicast. 
              This can be enabled in `config.py`.

## Settings

All configurations are commented in the `config.py` module. 


## Invocation 
```
python3 middleware.py < execution mode > [extra params]
```
