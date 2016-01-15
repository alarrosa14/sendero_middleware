import socket
import threading

import conf

from utils.StoppableThread import StoppableThread 
from utils.Utils import Utils
from device_manager.Device import Device


class DeviceManager:
    devices_connected = {}

    def worker():
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind(("0.0.0.0",conf.DeviceManager.REGISTRATION_PORT))
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            print("Listening for Device Registering UDP messages...")
            data, addr = sock_udp.recvfrom(100)
            print("Device sending message: {0} from IP/port: {1}/{2}".format(data, addr[0], addr[1]))
            
            if data[:8] == b'Device: ' and Utils.represents_int(data[8:]):
                device_id = int(data[8:])

                if device_id in DeviceManager.devices_connected:
                    print("A device with identifier {0} is already registered".format(device_id))
                else:
                    print("Will connect to {0}:{1}".format(addr[0], conf.DeviceManager.CONNECTION_PORT))
                    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    try:
                        sock_tcp.connect((addr[0], conf.DeviceManager.CONNECTION_PORT))
                    except Exception as e:
                        print("Something's wrong with %s. Exception type is %s" % (address, e))
                        sock_tcp.close()
                        continue
                    
                    device = Device(device_id=device_id, connection_socket=sock_tcp)

                    DeviceManager.devices_connected[device_id] = device
                    print("New device registered: {0}".format(DeviceManager.devices_connected[device_id]))

                    device.send_control_packet(True, 1, True)
            
    def listen_for_devices():
        print("Starting Device Registering thread...")
        t = threading.Thread(target=DeviceManager.worker)
        t.start()
