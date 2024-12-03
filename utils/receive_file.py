import os
import socket
import time

from utils.ftp_status_code import FTPStatusCode as FTPStatus

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
GENERAL_DOWNLOAD_DIR = SERVER_PUBLIC_PATH = os.path.abspath("../Downloads")
os.makedirs(GENERAL_DOWNLOAD_DIR, exist_ok=True)


def retrieve_file(command_conn: socket.socket, file_path):
    received = str(command_conn.recv(BUFFER_SIZE))
    time.sleep(0.2)
    print(received[2:5])
    if received[2:5] == str(FTPStatus.FILE_UNAVAILABLE):
        return
    transmit_port, filename, filesize = received.split(SEPARATOR)
    transmit_port = int(transmit_port.replace("b'", ""))
    filename = os.path.basename(filename)
    filesize = int(filesize.replace("'", ""))
    transmit_socket = socket.create_connection(("localhost", int(transmit_port)))
    with transmit_socket:
        with open(os.path.join(file_path, filename), "wb") as f:
            while True:
                bytes_read = transmit_socket.recv(BUFFER_SIZE)
                if bytes_read == b"EOF":
                    command_conn.send(f"{FTPStatus.FILE_STATUS_OK}".encode())
                    break
                f.write(bytes_read)


def download_file(conn, file_path=GENERAL_DOWNLOAD_DIR):
    retrieve_file(conn, file_path)
