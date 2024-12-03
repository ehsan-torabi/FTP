import pathlib
import socket
import time
from random import randint

from tqdm import tqdm

from .ftp_status_code import FTPStatusCode as FTPStatus

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def create_transmit_socket() -> (socket.socket, int):
    transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bind_success_flag = False
    port = 0
    while not bind_success_flag:
        try:
            port = randint(1024, 65535)
            transmit_socket.bind(("localhost", port))
            bind_success_flag = True
        except OSError:
            continue
    transmit_socket.listen(1)
    return transmit_socket, port


def send_file(file_path, command_conn):
    transmit_socket, transmit_port = create_transmit_socket()
    filename = ""
    filesize = 0
    try:
        file_path_object = pathlib.Path(file_path)
        if not file_path_object.absolute().is_file():
            raise Exception(f"File {file_path} is not a file")
        elif not file_path_object.exists():
            raise FileNotFoundError

        filename = file_path_object.name
        filesize = file_path_object.stat().st_size
        command_conn.send(f"{transmit_port}{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode())
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        command_conn.send(f"{FTPStatus.FILE_UNAVAILABLE}".encode())
        transmit_socket.close()
        return
    except Exception as exception:
        print(exception)
        command_conn.send(f"{FTPStatus.FILE_UNAVAILABLE}".encode())
        transmit_socket.close()
        return

    time.sleep(0.2)
    transmit_connection, addr = transmit_socket.accept()
    # start sending the file
    progress = tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with transmit_connection:
        with open(file_path_object, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    time.sleep(0.2)
                    transmit_connection.send(b"EOF")
                    break
                transmit_connection.send(bytes_read)
                progress.update(len(bytes_read))


def upload_file(conn, file_path):
    send_file(file_path, conn)
