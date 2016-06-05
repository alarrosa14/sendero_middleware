"""Return the square of n."""

from sendero_middleware import config
import struct
import time

SEQ_MAX = 256
ARTNET_HEADER = b'Art-Net\x00'


""" Initial timestamp """

def unsigned(x):
    return x & 0xFFFFFFFF

initial_millis = unsigned(int(round(time.time() * 1000)))

def millis():
    """Return the time in miliseconds elapsed from the application started."""
    return unsigned(int(round(time.time() * 1000)) - initial_millis)


def represents_int(s):
    """Try to cast s."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def increment_seq(current_seq):
    """ Increments the packet's sequence number taking into account the potencial unit overflow """
    return ((current_seq + 1) % SEQ_MAX)


def unpack_raw_artnet_packet(raw_data):
    """ Unpacks an ArtNet packet to create a Sendero-Wireless-Protocol packet """

    if struct.unpack('!8s', raw_data[:8])[0] != ARTNET_HEADER:
        print("Received a non Art-Net packet")
        return None

    packet = {}
    (packet['op_code'], packet['ver'], packet['sequence'], packet['physical'],
        packet['universe'], packet['length']) = struct.unpack(
        '!HHBBHH', raw_data[8:18])

    packet['data'] = struct.unpack(
        '{0}s'.format(int(packet['length'])),
        raw_data[18:18 + int(packet['length'])])[0]

    return packet


def sendero_data_packet(pt, seq, flags, payload):
    # XXX: This packet should have the SENDERO header
    """
    Constructs a Sendero-Wireless-Protocol data packet 

    previouspacket_timestamp is useful when multiple multicast groups
    are enabled.
    """
    # XXX: This packet should have the SENDERO header
    return struct.pack("<IBB{0}B".format(len(payload)),
                       unsigned(pt),
                       seq, flags,
                       *payload)


def sendero_control_packet():
    """ Constructs a Sendero-Wireless-Protocol control packet """
    # XXX: Pending - Unused for the moment.
    return None
