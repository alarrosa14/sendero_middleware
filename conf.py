class DeviceManager:
    REGISTRATION_PORT = 8888
    CONNECTION_PORT = 8889

DEFAULT_DEVICE_MANAGED_PIXELS_QTY = 8

GLOBAL_PIXELS_QTY = 24

STATS_REQUEST_INTERVAL = 5
KEEP_ALIVE_INTERVAL = 10

DEVICE_CONFIG = {
    1: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 0
    },
    2: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 8 * 3
    },
    3: {
        "Device.managedPixelsQty": 8,
        "Device.firstPixel": 16 * 3
    }
}

GLOBAL_CONFIG = {
    "Global.pixelsQty": GLOBAL_PIXELS_QTY,
    "ControlServer.keepAliveSeconds": KEEP_ALIVE_INTERVAL * 2
}


def is_allowed_device(device_id):
    return device_id in DEVICE_CONFIG
