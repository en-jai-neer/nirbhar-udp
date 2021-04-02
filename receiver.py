from socket import socket, AF_INET, SOCK_DGRAM, error
import time
import packet_utils
from threading import Thread, Lock
from copy import deepcopy

TIMEOUT = 1  # 1 sec
PACKET_SIZE = 1000  # in bytes
WINDOW_SIZE = 1000
BLOCKING_SLEEP = 0.00001
BUFFER_SIZE = 1024
MAX_TRIES = 1000


class Receiver:

    def __init__(self, self_ip, self_port, dest_ip, dest_port):
        self.receive_buffer = {}
        self.sent_to_app = set()
        self.receive_base = 0
        self.self_ip = self_ip
        self.self_port = self_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.conn_close_time = 0
        self.connection_alive = False
        self.fin_acked = False

        # locks
        self.receive_buffer_lock = Lock()

        # socket init
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        try:
            self.sock.bind((self_ip, self_port))
            print("DEBUG: Bound to ", (self_ip, self_port))
            self.connection_alive = True
        except error as exc:
            print("DEBUG: Error binding to ", (self_ip, self_port), exc)
            self.connection_alive = False

        # start thread to receive data packets
        self.receiving_thread = Thread(target=self.__run_listener)
        self.receiving_thread.setDaemon(True)
        self.receiving_thread.start()

    def __run_listener(self):
        print("listening for packets at {}:".format(self.sock.getsockname()))
        while True:
            packet = packet_utils.receive_pkt(self.sock, BUFFER_SIZE)

            if packet is None:
                # print("packet may be corrupted")
                continue

            if packet.data_type == "FIN_ACK":
                # print("FIN_ACK is received")
                self.fin_acked = True
                break

            if packet.data_type == "DATA":
                # print("packet received for: ", packet.seq)
                if packet.is_payload_corrupt():
                    # print("packet is corrupted")
                    continue
                if packet.seq < self.receive_base or packet.seq in self.receive_buffer.keys() or packet.seq in self.sent_to_app:
                    # print("packet: ", packet.seq, " already received")
                    packet_utils.send_pkt(self.sock, packet_utils.create_ack(packet.seq), self.dest_ip, self.dest_port)
                    continue
                if packet.seq >= self.receive_base + WINDOW_SIZE:
                    continue
                if self.receive_base <= packet.seq < self.receive_base + WINDOW_SIZE:
                    # print("storing packet ", packet.seq, " in buffer")
                    with self.receive_buffer_lock:
                        self.receive_buffer[packet.seq] = packet
                        packet_utils.send_pkt(self.sock, packet_utils.create_ack(packet.seq), self.dest_ip, self.dest_port)

            # print("# packets in buffer: ", len(self.receive_buffer))
            # print(self.connection_alive)
            if not self.connection_alive:
                break

    def __get_buffered_data(self):
        if not self.receive_buffer:
            return None

        with self.receive_buffer_lock:
            seq = min(self.receive_buffer, default=0)
            if seq in self.sent_to_app:
                del self.receive_buffer[seq]
                return None
            if seq == self.receive_base:
                # print("packet to application: ", seq)
                self.sent_to_app.add(seq)
                payload = self.receive_buffer[seq].payload
                del self.receive_buffer[seq]
                self.receive_base += 1
                return payload
            else:
                return None

    def receive(self):
        while True:
            data = self.__get_buffered_data()
            if data is not None:
                data = deepcopy(data)
                return data
            time.sleep(BLOCKING_SLEEP)

    def close(self):
        time.sleep(TIMEOUT)
        count = 0
        while self.fin_acked is False and count < MAX_TRIES:
            packet_utils.send_pkt(self.sock, packet_utils.create_fin(), self.dest_ip, self.dest_port)
            count += 1

        self.connection_alive = False
        time.sleep(TIMEOUT)
        self.conn_close_time = time.time()
        return True
