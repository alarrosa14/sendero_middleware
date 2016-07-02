import socket
import time
from sendero_middleware import config, utils
from socket import (
	socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP, IPPROTO_IP, IP_MULTICAST_TTL)

multicast_group_data = {
	0: {
		"pixels": config.GLOBAL_PIXELS_QTY, 
		"ip": config.STREAMING_MULTICAST_DST_BASE_IP,
		"first_pixel": 0
	}
}

# calculate multicast groups

if config.MULTICAST_GROUPS_QTY != 1:
	ideal_qty = config.GLOBAL_PIXELS_QTY/config.MULTICAST_GROUPS_QTY
	sorted_device_configs = config.get_sorted_device_configs()

	pixels_count = 0
	group = 0
	first_group_pixel = 0
	for k, v in sorted_device_configs:
		print(k, v)
		managed_pixels = v[config.DeviceKeys.MANAGED_PIXELS_QTY]
		pixel_index = v[config.DeviceKeys.FIRST_PIXEL]
		pixels_count += managed_pixels
		if pixels_count - first_group_pixel >= ideal_qty:
			# update group dataconfig
			print("creating group " + str(group))
			multicast_group_data[group] = {}
			multicast_group_data[group]["pixels"] = pixels_count - first_group_pixel
			multicast_group_data[group]["first_pixel"] = first_group_pixel
			group += 1
			first_group_pixel = pixels_count

	if pixels_count < config.GLOBAL_PIXELS_QTY:
		multicast_group_data[group] = {}
		multicast_group_data[group]["pixels"] = pixels_count - first_group_pixel
		multicast_group_data[group]["first_pixel"] = first_group_pixel
		
	print(group)

groups_qty = len(multicast_group_data.items())
sorted_multicast_group_data = sorted(multicast_group_data.items(), key=lambda x: x[0])

print(sorted_multicast_group_data)

def get_multicast_ip_for_group(id):
	mip = config.STREAMING_MULTICAST_DST_BASE_IP
	last_point_index = mip.rfind('.') + 1
	return mip[:last_point_index] + str(int(mip[last_point_index:]) + id)

# calculate multicast groups ips
for group, data in multicast_group_data.items():
	ip = get_multicast_ip_for_group(group)
	data["ip"] = ip

print("\nPartition in {0} multicast groups.\n{1}\n".format(len(multicast_group_data.items()), multicast_group_data))

# create socket
sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)

def get_multicast_pixels_qty_for_device(id):
	group = get_multicast_group_for_device(id)
	print(multicast_group_data[group])
	return multicast_group_data[group]["pixels"]

def get_multicast_first_pixel_for_device(id):
	group = get_multicast_group_for_device(id)
	group_first_pixel = multicast_group_data[group]["first_pixel"]
	return group_first_pixel

def get_multicast_group_for_device(id):
	first_pixel_of_device = config.DEVICE_CONFIG[id][config.DeviceKeys.FIRST_PIXEL]
	for group, data in sorted_multicast_group_data:
		first_group_pixel = data["first_pixel"]
		if first_pixel_of_device < first_group_pixel:
			return group - 1
		elif first_pixel_of_device == first_group_pixel:
			return group
	return sorted_multicast_group_data[-1][0]

def get_playback_time_delay_for_device(id):
	group = get_multicast_group_for_device(id)
	return config.PLAYBACK_TIME_DELAY - group*config.DELAY_BETWEEN_MULTICAST_PACKETS*1000

def get_multicast_ip_for_device(id):
	return multicast_group_data[get_multicast_group_for_device(id)]["ip"]

N = 0
suma = 0
mean = 0
prev = 0
def send_streaming_packet(seq, flags, payload):
	global N
	global mean
	global suma
	global prev
	currMillis = utils.millis()
	if groups_qty == 1:
		packet = utils.sendero_data_packet(
			currMillis + config.PLAYBACK_TIME_DELAY, seq, flags, payload)
		sock.sendto(packet, (multicast_group_data[0]["ip"], config.STREAMING_DST_PORT))
	else:
		multicast_payloads = []

		last_pixel_index = 0
		for group, data in sorted_multicast_group_data:
			if group == 0:
				continue
			pixel_index = data["first_pixel"]
			multicast_payloads.append(payload[last_pixel_index*3:pixel_index*3])
			last_pixel_index = pixel_index

		# last partition	
		multicast_payloads.append(payload[last_pixel_index*3: config.GLOBAL_PIXELS_QTY*3])

		group = 0
		offset = 0
		for m_payload in multicast_payloads:
			pt = utils.millis() + config.PLAYBACK_TIME_DELAY
			packet = utils.sendero_data_packet(pt, seq, flags, m_payload)
			sock.sendto(packet, (multicast_group_data[group]["ip"], config.STREAMING_DST_PORT))
			if group < config.MULTICAST_GROUPS_QTY - 1:
				time.sleep(config.DELAY_BETWEEN_MULTICAST_PACKETS)
			group += 1

	N += 1
	if N > 1:
		suma += currMillis - prev
	mean = suma / N
	prev = currMillis
