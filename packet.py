# Jain Jai Sandeep - 2017A7PS1585H
# Prateek Hiranandani - 2017B4A70578H
# Sahil Nair - 2017B5A71317H
# Jatin Arora - 2018A7PS0551H
# Rusabh Rakesh Parikh - 2018A7PS1217H

from zlib import adler32


class Packet:
    def __init__(self, payload, seq, data_type):
        self.payload = payload
        self.seq = seq
        self.data_type = data_type
        self.checksum = adler32(payload + str(seq).encode('utf-8')) & 0xffffffff

    def is_payload_corrupt(self):
        return (adler32(self.payload + str(self.seq).encode('utf-8')) & 0xffffffff) != self.checksum
