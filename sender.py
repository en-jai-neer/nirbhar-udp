import signal
from socket import socket, AF_INET, SOCK_DGRAM, SHUT_RDWR
import time
from threading import Thread, Lock
from collections.abc import Hashable
from copy import deepcopy
import packet_utils
import sys
import os
import traceback

TIMEOUT = 1  # 1 sec
PACKET_SIZE = 1000  # in bytes
MAX_TRIES = 1000  # retransmission count
WINDOW_SIZE = 1000
BLOCKING_SLEEP = 0.00001
BUFFER_SIZE = 1024


class Sender:

    def __init__(self, self_ip, self_port, dest_ip, dest_port):
        self.send_buffer = {}
        self.retry_count = {}
        self.acked = set()
        self.send_base = 0
        self.self_ip = self_ip
        self.self_port = self_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.seq_num = 0
        self.conn_close_time = 0
        self.connection_alive = False

        # locks
        self.send_buffer_lock = Lock()
        self.seq_num_lock = Lock()
        self.sock_send_lock = Lock()
        self.send_base_lock = Lock()

        # socket init
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        try:
            self.sock.bind((self_ip, self_port))
            print("DEBUG: Bound to ", (self_ip, self_port))
            self.connection_alive = True
        except:
            print("DEBUG: Error binding to ", (self_ip, self_port))
            self.connection_alive = False

        # start thread to receive ACKs
        self.receiving_thread = Thread(target=self.__run_listener)
        self.receiving_thread.setDaemon(True)
        self.receiving_thread.start()

        # start thread to retransmit data packets
        self.retransmitting_thread = Thread(target=self.__run_retransmitter)
        self.retransmitting_thread.setDaemon(True)
        self.retransmitting_thread.start()

    def __run_listener(self):
        print("listening for packets at {}:".format(self.sock.getsockname()))
        while True:
            # print("Checking for ACKs")
            packet = packet_utils.receive_pkt(self.sock, BUFFER_SIZE)

            if packet is None:
                # print("packet may be corrupted")
                continue

            if packet.data_type == "FIN":
                with self.send_buffer_lock:
                    self.send_buffer.clear()
                # print("FIN received")
                self.send_fin_ack()
                break

            if packet.data_type == "ACK":
                # print("received ACK for: ", packet.seq)
                if packet.seq < self.send_base:
                    # print("ACK OUT OF WINDOW: Ignoring ACK ", packet.seq)
                    continue

                # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                with self.send_buffer_lock:
                    # print("# packets in buffer: ", len(self.send_buffer))
                    if packet.seq in self.send_buffer.keys():
                        del self.send_buffer[packet.seq]

                self.acked.add(packet.seq)
                with self.send_base_lock:
                    first_not_acked = self.send_base
                    for i in range(self.send_base, self.send_base+WINDOW_SIZE+2):
                        if i not in self.acked:
                            first_not_acked = i
                            break
                    self.send_base = first_not_acked
            if self.connection_alive is False:
                os.kill(os.getpid(), signal.SIGINT)
                sys.exit()
            # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    def __send(self, packet, retransmit=False):
        if not retransmit:
            with self.send_buffer_lock:
                self.send_buffer[packet.seq] = (packet, time.time())

        try:
            with self.sock_send_lock:
                packet_utils.send_pkt(self.sock, packet, self.dest_ip, self.dest_port)
        except Exception as _:
            return

    def is_send_buffer_full(self):
        # print("in send buffer")
        with self.seq_num_lock:
            # print("seqnum: ", self.seq_num)
            # print("send base: ", self.send_base)
            if self.seq_num <= self.send_base + WINDOW_SIZE:
                seq = self.seq_num
                self.seq_num += 1
                return seq
            else:
                return -1

    def send(self, data):
        if not isinstance(data, Hashable):
            raise Exception("Data object is not hashable.")

        seq = -1
        while True:
            seq = self.is_send_buffer_full()
            if seq == -1:
                time.sleep(BLOCKING_SLEEP)
            else:
                break

        data = deepcopy(data)
        packet = packet_utils.create_data_pkt(data, seq)
        self.__send(packet)

    def __run_retransmitter(self):
        try:
            while True:
                time.sleep(TIMEOUT)

                if self.connection_alive is False and not self.send_buffer:
                    return
                # print("Checking for timed out packets")
                with self.send_buffer_lock:
                    # print("Retransmitting thread aquired the lock...")
                    for seq in self.send_buffer.keys():
                        if seq not in self.retry_count.keys():
                            self.retry_count[seq] = 0

                        (packet, pkt_transmission_time) = self.send_buffer[seq]
                        time_now = time.time()
                        if (time_now - pkt_transmission_time) >= TIMEOUT:
                            if self.retry_count[seq] > MAX_TRIES:
                                # print("********** Connection Broken **********")
                                # print("Stopping File Transfer")
                                self.force_close()
                            self.send_buffer[packet.seq] = (packet, time.time())
                            # print("Retransmitting packet: ", seq)
                            self.retry_count[seq] += 1
                            self.__send(packet, retransmit=True)

                    # print("# packets in buffer: ", len(self.send_buffer))
        except Exception:
            traceback.print_exc()

    def send_fin_ack(self):
        for i in range(MAX_TRIES):
            packet_utils.send_pkt(self.sock, packet_utils.create_fin_ack(), self.dest_ip, self.dest_port)

        self.close()

    def close(self):
        while self.send_buffer:
            time.sleep(BLOCKING_SLEEP)

        self.connection_alive = False
        time.sleep(TIMEOUT)
        print(self.receiving_thread.is_alive())
        self.conn_close_time = time.time()
        return True

    def force_close(self):
        self.connection_alive = False
        self.conn_close_time = time.time()
        time.sleep(5)
        os.kill(os.getpid(), signal.SIGINT)
        sys.exit()

