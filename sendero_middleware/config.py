
"""
Configuration Module

Stores all the configurable settings.
Sections:
    - General Settings
    - Control Server
    - Streaming
    - Device Management
"""

# #########################################
# General Settings
# #########################################

UDP_IP = "0.0.0.0"
UDP_PORT = 7777

BROADCAST_PORT = 7788
BROADCAST_IP = "255.255.255.255"

# #########################################
# Control Server
# #########################################

STATS_REQUEST_INTERVAL = 3600
KEEP_ALIVE_INTERVAL = 10

REGISTRATION_PORT = 8888
CONNECTION_PORT = 8889

# #########################################
# Streaming
# #########################################

ARTNET_MAX_PACKAGE_LEN = 1024

PLAYBACK_TIME_DELAY = 200

SEQ_MAX = 256

ARTNET_HEADER = b'Art-Net\x00'


# #########################################
# Device Management
# #########################################

DEFAULT_DEVICE_MANAGED_PIXELS_QTY = 8

GLOBAL_PIXELS_QTY = 91

DEVICE_CONFIG = {
    1: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 0
    },
    2: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 0
    },
    3: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 0
    }
}

GLOBAL_CONFIG = {
    "Global.pixelsQty": GLOBAL_PIXELS_QTY,
    "ControlServer.keepAliveSeconds": KEEP_ALIVE_INTERVAL * 2
}


def is_allowed_device(device_id):
    """
    Returns TRUE if the device with id = device_id is into the DEVICE_CONFIG dict.
    FALSE in other case.
    """
    return device_id in DEVICE_CONFIG
