# Jain Jai Sandeep - 2017A7PS1585H
# Prateek Hiranandani - 2017B4A70578H
# Sahil Nair - 2017B5A71317H
# Jatin Arora - 2018A7PS0551H
# Rusabh Rakesh Parikh - 2018A7PS1217H

import time
import sys
from sender import Sender
from receiver import Receiver
import traceback


def ftp_sender():
    try:
        print("Sender starting")
        data = "Sample data to be sent over by the Nirbhar protocol" * 15
        data = data.encode('utf-8')
        sender = Sender('localhost', 12345, 'localhost', 12346)
        if sender.connection_alive:
            print("-----------Established Connection-----------")
        else:
            print("-----------Error Establishing Connection-----------")
            return
        data_size = 0

        start_time = time.time()

        while True:
            sender.send(data)
            data_size += sys.getsizeof(data)
            print("sent: ", data_size, " Bytes")
            print("sent: {} Bytes - buffer: ({})".format(data_size, len(sender.send_buffer)))
            # print("%%%%%%%%%%%%%%%% Time Elapsed: ", time.time() - start_time)
            sys.stdout.flush()
            if (time.time() - start_time) >= 60:
                print("\ntest finished")
                message = "end"
                sender.send(message.encode('utf-8'))
                res = sender.close()
                print('res ', res)
                print('\ndone sending')
                return

    except Exception:
        traceback.print_exc()


def ftp_receiver():
    try:
        receiver = Receiver('localhost', 12346, 'localhost', 12345)
        if receiver.connection_alive:
            print("-----------Established Connection-----------")
        else:
            print("-----------Error Establishing Connection-----------")
            return
        time_start = time.time()
        data_size = 0
        bandwidth = 0
        while True:
            data = receiver.receive()
            if data.decode('utf-8') == "end":
                print("\ntest finished")
                break
            data_size += sys.getsizeof(data)

            bandwidth = data_size / (time.time() - time_start)
            print("bandwidth: {} B/s - buffer: ({})".format(str(bandwidth)[0:10], len(receiver.receive_buffer)))
            print("data received: ", data_size)
            sys.stdout.flush()

        res = receiver.close()
        print('res', res)
    except Exception:
        traceback.print_exc()


mode = input("mode (1 - sender, 2 - receiver): ")
if mode == '1':
    ftp_sender()
else:
    ftp_receiver()
