"""
Configuration Module.

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

"""
Used only when sending simulated 'sin' and 'flash' streams.
"""
FRAMES_PER_SECOND = 30
FRAME_RATE = 1.0 / FRAMES_PER_SECOND


"""
Sendero Middleware address where ArtNet packets must be sent.
Only useful with artnet stream mode ('devserver artnet' or 'prodserver').
"""
UDP_IP = "0.0.0.0"
UDP_PORT = 7777

# #########################################
# Control Server
# #########################################

"""
Sets how often the middleware requests the device statistics.
"""
STATS_REQUEST_INTERVAL = 3600

"""
Sets how often the middleware sends a 'keep alive' packet to the devices.
"""
KEEP_ALIVE_INTERVAL = 30

"""
UDP port where devices request for connection.
This message is sent via UDP broadcast.
"""
REGISTRATION_PORT = 8888

"""
TCP port where the devices should send the statistics.
"""
CONNECTION_PORT = 8889

# #########################################
# Streaming
# #########################################

"""
In case multicast is enabled, this settings sets the quantity of groups.
"""
MULTICAST_GROUPS_QTY = 1

"""
Some times the devices miss broadcast packets if they are sent consecutively.
This settings sets the delay between multicast packets.
0.01 has proved to be enough.
"""
DELAY_BETWEEN_MULTICAST_PACKETS = FRAME_RATE / MULTICAST_GROUPS_QTY

"""
The port where the devices listens for the stream.
"""
STREAMING_DST_PORT = 7788

"""
Broadcast IP for the stream.
"""
STREAMING_BROADCAST_DST_IP = "255.255.255.255"

"""
Multicast base IP for groups.
Consecutive groups are setted automatically begining from this IP.
"""
STREAMING_MULTICAST_DST_BASE_IP = "224.0.0.116"


"""
Frames playout time is setted in the middleware and sent as a configuration
header to devices. This setting is the delay time in milliseconds to
reproduce the frame starting from the moment it is processed by the middleware.
"""
PLAYBACK_TIME_DELAY = 100  # ms


# #########################################
# Clock Sync
# #########################################

OFFSET_SIGMA = 3  # ms
EXPIRATION_PERIOD = 60 * 1000  # ms
OFFSET_MEAN_CALIBRATION_CONSECUTIVE_PACKETS = 2 * FRAMES_PER_SECOND
OFFSET_MEAN_CALIBRATION_DERIVATIVE_THRESHOLD = 0.001
FIRST_PACKETS_IGNORE_QTY = 3 * FRAMES_PER_SECOND

# #########################################
# Device Management
# #########################################


class DeviceKeys:
    """
    Device specific settings.

    These constants are the device specific configurable settings.
    """

    """
    The quantity of pixel that a specific device manages.
    """
    MANAGED_PIXELS_QTY = "Device.managedPixelsQty"

    """
    The first pixel in the stream that a specific device must reproduce.
    """
    FIRST_PIXEL = "Device.firstPixel"

    """
    Some LED stripes receive this information in a different order.
    This configuration is used to specify the color order for each pixel.
    """
    COLOR_ORDER = "Device.colorOrder"

    PLAYBACK_DELAY = "Streaming.playbackTimeDelay"

    #########################################################################
    """
    These configurations are set automatically and shouldn't be set manually.
    """
    MULTICAST_GROUP_IP = "Streaming.multicastGroupIp"
    STREAMING_PIXELS_QTY = "Streaming.pixelsQty"
    MULTICAST_GROUP_FIRST_PIXEL = "Streaming.multicastGroupFirstPixel"
    #########################################################################

"""
The total amount of pixels to which color data is going to be sent for.
"""

GLOBAL_PIXELS_QTY = 488

# Default color order is GRB.
# Set DeviceKeys.COLOR_ORDER if you need to change this
# DEVICE_CONFIG = {
#     8: {
#         DeviceKeys.FIRST_PIXEL: 0,
#         DeviceKeys.MANAGED_PIXELS_QTY: 8,
#         DeviceKeys.COLOR_ORDER: ['BRG']*8
#     }
# }

# # calculate global pixels qty

# GLOBAL_PIXELS_QTY = 0
# for k, v in DEVICE_CONFIG.items():
#     GLOBAL_PIXELS_QTY += v[DeviceKeys.MANAGED_PIXELS_QTY]

# print(GLOBAL_PIXELS_QTY)

"""
Here is where device specific behaviour is configured using DeviceKeys
DEVICE_CONFIG key must be the 'deviceId' as number
"""
DEVICE_CONFIG = {}

device = 0
for pixel in range(0, GLOBAL_PIXELS_QTY, 8):
    DEVICE_CONFIG[device] = {
        DeviceKeys.FIRST_PIXEL: pixel, 
        DeviceKeys.MANAGED_PIXELS_QTY: 8,
        DeviceKeys.COLOR_ORDER: ['BRG'] * 8
    }
    device += 1


"""
GLOBAL_DEVICES_CONFIGS are setted with most of the previous configs.
Should not be edited.
"""
GLOBAL_DEVICES_CONFIGS = {
    "Global.pixelsQty": GLOBAL_PIXELS_QTY,
    "ControlServer.keepAliveSeconds": KEEP_ALIVE_INTERVAL,
    # "Streaming.playbackTimeDelay": PLAYBACK_TIME_DELAY,
    "ClockSync.offsetSigma": OFFSET_SIGMA,
    "ClockSync.expirationPeriod": EXPIRATION_PERIOD,
    "ClockSync.offsetMeanCalibrationConsecutivePackets":
        OFFSET_MEAN_CALIBRATION_CONSECUTIVE_PACKETS,
    "ClockSync.offsetMeanCalibrationDerivativeThreshold":
        OFFSET_MEAN_CALIBRATION_DERIVATIVE_THRESHOLD,
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
    """Return the device configs sorted by key."""
    return get_sorted_list_from_dictionary(DEVICE_CONFIG)

def get_sorted_list_from_dictionary(dict):
    return sorted(dict.items(), key=lambda x: x[0])
