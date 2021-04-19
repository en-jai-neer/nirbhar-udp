# Jain Jai Sandeep - 2017A7PS1585H
# Prateek Hiranandani - 2017B4A70578H
# Sahil Nair - 2017B5A71317H
# Jatin Arora - 2018A7PS0551H
# Rusabh Rakesh Parikh - 2018A7PS1217H

from packet import Packet
import pickle
import traceback


def create_ack(seq):
    packet = Packet(bytes("", 'utf-8'), seq, "ACK")
    return packet


def create_data_pkt(data, seq):
    packet = Packet(data, seq, "DATA")
    return packet


def create_fin():
    packet = Packet(bytes("", 'utf-8'), -1, "FIN")
    return packet


def create_fin_ack():
    packet = Packet(bytes("", 'utf-8'), -1, "FIN_ACK")
    return packet


def receive_pkt(sock, buffer_size):
    try:
        packet, address = sock.recvfrom(buffer_size)
        packet = pickle.loads(packet)
        # print("received packet: ", packet.payload, " ", packet.seq, " data_type: ", packet.data_type, " \n")
        # print("received from IP: ", address)
        return packet
    except Exception:
        # traceback.print_exc()
        return None


def send_pkt(sock, packet, dest_ip, dest_port):
    try:
        sock.sendto(pickle.dumps(packet), (dest_ip, dest_port))
        # print("Sent Packet: ", packet.seq)
    except Exception:
        traceback.print_exc()
        print("DEBUG: Error sending to ", (dest_ip, dest_port))
