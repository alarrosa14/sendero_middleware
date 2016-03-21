"""
Configuration Module.

Stores all the configurable settings.
Sections:
    - General Settings
    - Control Server
    - Streaming
    - Device Management
"""

import operator

# #########################################
# General Settings
# #########################################

FRAMES_PER_SECOND = 24
FRAME_RATE = 1.0/FRAMES_PER_SECOND
UDP_IP = "0.0.0.0"
UDP_PORT = 7777

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

MULTICAST_GROUPS_QTY = 1
DELAY_BETWEEN_MULTICAST_PACKETS = 0.01
STREAMING_DST_PORT = 7788
STREAMING_BROADCAST_DST_IP = "255.255.255.255"
STREAMING_MULTICAST_DST_BASE_IP = "224.0.0.116"

ARTNET_MAX_PACKAGE_LEN = 1024
PLAYBACK_TIME_DELAY = 200
SEQ_MAX = 256
ENABLE_CLOCK_EXPIRATION_FLAG = True
CLOCK_EXPIRATION_PERIOD = 3000
ARTNET_HEADER = b'Art-Net\x00'

# #########################################
# Clock Sync
# #########################################

OFFSET_SIGMA = 3 # ms
EXPIRATION_PERDIOD = 60*1000 # ms
OFFSET_MEAN_CALIBRATION_CONSECUTIVE_PACKETS = 2*FRAMES_PER_SECOND
OFFSET_MEAN_CALIBRATION_DERIVATIVE_THRESHOLD = 0.001
FIRST_PACKETS_IGNORE_QTY = 3*FRAMES_PER_SECOND

# #########################################
# Device Management
# #########################################

class DeviceKeys:
    MANAGED_PIXELS_QTY = "Device.managedPixelsQty"
    FIRST_PIXEL = "Device.firstPixel"
    MULTICAST_GROUP_IP = "Streaming.multicastGroupIp"
    STREAMING_PIXELS_QTY = "Streaming.pixelsQty"
    MULTICAST_GROUP_FIRST_PIXEL = "Streaming.multicastGroupFirstPixel"


DEFAULT_DEVICE_MANAGED_PIXELS_QTY = 8

DEVICE_CONFIG = {
    6: {
        DeviceKeys.FIRST_PIXEL: 0,
        DeviceKeys.MANAGED_PIXELS_QTY: 50,
    },
    7: {
        DeviceKeys.FIRST_PIXEL: 50,
        DeviceKeys.MANAGED_PIXELS_QTY: 41,
    }
}

# calculate global pixels qty

GLOBAL_PIXELS_QTY = 0
for k, v in DEVICE_CONFIG.items():
    GLOBAL_PIXELS_QTY += v[DeviceKeys.MANAGED_PIXELS_QTY]

print(GLOBAL_PIXELS_QTY)

GLOBAL_CONFIG = {
    "Global.pixelsQty": GLOBAL_PIXELS_QTY,
    "ControlServer.keepAliveSeconds": KEEP_ALIVE_INTERVAL * 2,
    "Streaming.playbackTimeDelay": PLAYBACK_TIME_DELAY,
    "ClockSync.offsetSigma": OFFSET_SIGMA,
    "ClockSync.expirationPeriod": EXPIRATION_PERDIOD,
    "ClockSync.offsetMeanCalibrationConsecutivePackets": OFFSET_MEAN_CALIBRATION_CONSECUTIVE_PACKETS,
    "ClockSync.offsetMeanCalibrationDerivativeThreshold": OFFSET_MEAN_CALIBRATION_DERIVATIVE_THRESHOLD,
    "ClockSync.firstPacketsIgnoreQty": FIRST_PACKETS_IGNORE_QTY
}


def is_allowed_device(device_id):
    """
    Device is allowed.

    Return TRUE if the device with id = device_id is into the DEVICE_CONFIG
    dict. Return FALSE in other case.
    """
    return device_id in DEVICE_CONFIG

def get_sorted_device_configs():
    return sorted(DEVICE_CONFIG.items(), key=lambda x: x[0])
