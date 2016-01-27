import socket
import threading
import time

import conf

from utils.StoppableThread import StoppableThread 
from utils.Utils import Utils
from device_manager import millis
from device_manager.Device import Device

class DeviceManager:
    devices_connected = {}
    lock = threading.Lock()

    def addDevice(device_id,device):
        DeviceManager.lock.acquire()
        DeviceManager.devices_connected[device_id] = device
        DeviceManager.lock.release()

    def deviceConnectedQty():
        res = 0
        DeviceManager.lock.acquire()
        res = len(DeviceManager.devices_connected)
        DeviceManager.lock.release()
        return res


    def device_server_worker():
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind(("0.0.0.0",conf.DeviceManager.REGISTRATION_PORT))
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            print("Listening for Device Registering UDP messages...")
            data, addr = sock_udp.recvfrom(100)
            
            if data[:8] == b'Device: ' and Utils.represents_int(data[8:]):
                print("Device sending message: {0} from IP/port: {1}/{2}".format(data, addr[0], addr[1]))
                device_id = int(data[8:])

                DeviceManager.lock.acquire()
                if device_id in DeviceManager.devices_connected:
                    print("A device with identifier {0} is already registered".format(device_id))
                    print("Reconnecting...")
                    device = DeviceManager.devices_connected.pop(device_id, 0)
                    if device:
                        del device
                DeviceManager.lock.release()

                print("Will connect to {0}:{1}".format(addr[0], conf.DeviceManager.CONNECTION_PORT))
                sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    sock_tcp.connect((addr[0], conf.DeviceManager.CONNECTION_PORT))
                except Exception as e:
                    print("Something's wrong with %s. Exception type is %s" % (addr[0], e))
                    sock_tcp.close()
                    continue
                
                device = Device(device_id=device_id, connection_socket=sock_tcp, active=True)

                DeviceManager.addDevice(device_id,device)
                print("New device registered: {0}".format(device))
                    

    def control_server_worker():
        current_device_index = 0
        while True:
            time.sleep(5)
            
            

            """
            if DeviceManager.deviceConnectedQty() > 0:
                DeviceManager.lock.acquire()
                device = list(DeviceManager.devices_connected.values())[current_device_index]
                current_device_index = (current_device_index + 1) % len(DeviceManager.devices_connected)
                DeviceManager.lock.release()
            """


    def listen_for_devices():
        print("Starting Device Registering thread...")
        t = threading.Thread(target=DeviceManager.device_server_worker)
        t.start()

    def start_control_server():
        print("Starting Control Server thread...")
        t = threading.Thread(target=DeviceManager.control_server_worker)
        t.start()
