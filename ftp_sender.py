# Jain Jai Sandeep - 2017A7PS1585H
# Prateek Hiranandani - 2017B4A70578H
# Sahil Nair - 2017B5A71317H
# Jatin Arora - 2018A7PS0551H
# Rusabh Rakesh Parikh - 2018A7PS1217H

from sender import Sender
import time
from os import path
from tqdm import tqdm
import traceback

BUFFER_SIZE = 512


def server():
    try:
        file_path = input("Enter the file path of the file that you want to send\n")
        dest_file_path = input("Enter the file path at the receiver where you want to store the file\n")
        time.sleep(5)

        f = open(file_path, 'rb')
        file_size = path.getsize(file_path)

        print(f"sending {file_path} to client")
        print(f"filesize: {file_size}")

        sender = Sender('localhost', 12345, 'localhost', 12346)
        if sender.connection_alive:
            print("-----------Established Connection-----------")
        else:
            print("-----------Error Establishing Connection-----------")

        data = dest_file_path + "%%$$##" + str(file_size)
        data = data.encode('utf-8')
        # print(data)
        sender.send(data)
        data_sent = 0
        with tqdm(total=file_size) as pbar:
            data = f.read(BUFFER_SIZE)
            while data:
                sender.send(data)
                # print(f"sent: {data_sent} / {filesize}", end="\r")
                update_value = min(BUFFER_SIZE, file_size - data_sent)
                data_sent += BUFFER_SIZE
                pbar.update(update_value)

                data = f.read(BUFFER_SIZE)

        f.close()
        res = sender.close()
        print('res', res)
        print('\ndone sending')
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    server()
