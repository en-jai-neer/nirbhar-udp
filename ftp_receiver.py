from receiver import Receiver
import time
from tqdm import tqdm
import traceback


def client():
    try:
        receiver = Receiver('localhost', 12346, 'localhost', 12345)
        if receiver.connection_alive:
            print("-----------Established Connection-----------")
        else:
            print("-----------Error Establishing Connection-----------")
            return

        time.sleep(2)
        print("\nwaiting for another file...")
        resp = receiver.receive()
        resp = resp.decode('utf-8')
        special_str_ind = resp.find("%%$$##")
        if special_str_ind == -1:
            print("Handshake packet is not properly formulated")
        file_path = resp[:special_str_ind]
        file_size = int(resp[special_str_ind+6:])
        print(f"filename: {file_path}, filesize: {file_size}")

        data_recv = 0

        with open(file_path, 'wb+') as f:
            with tqdm(total=file_size) as pbar:
                while True:
                    data = receiver.receive()
                    data_recv += len(data)
                    f.write(data)
                    # print(f"received: {data_recv} / {filesize}", end="\r")
                    pbar.update(len(data))
                    if data_recv >= file_size:
                        break

        res = receiver.close()
        print(res)
        print("\ntransfer complete")
    except KeyboardInterrupt:
        traceback.print_exc()


if __name__ == "__main__":
    client()
