## Nirbhar UDP

The underlying protocol doesn't have any dependency other than python3.
The file transfer application uses "tqdm" library to display progress bar.

### File Transfer

  terminal 1:
    $ python3 ftp_receiver.py

  terminal 2:
    $ python3 ftp_sender.py

#### description:
The sender will ask for the path of the file that needs to be sent.

It will then ask for the location where we want to store the file at the receiver.

	NOTE: Receiver should be started first in all the cases.

### Changes made during implementation

The sequence number at sender and receiver will start from 0

On creating an instance of the Sender/Receiver class, the execution of sender/receiver will begin
