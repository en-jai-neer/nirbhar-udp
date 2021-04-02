from zlib import adler32


class Packet:
    def __init__(self, payload, seq, data_type):
        self.payload = payload
        self.seq = seq
        self.data_type = data_type
        self.checksum = adler32(payload + str(seq).encode('utf-8')) & 0xffffffff

    def is_payload_corrupt(self):
        return (adler32(self.payload + str(self.seq).encode('utf-8')) & 0xffffffff) != self.checksum
