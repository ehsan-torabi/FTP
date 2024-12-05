import pathlib
import socket
import time
from random import randint

from tqdm import tqdm

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


def get_file_info(file_path):
    file_path_object = pathlib.Path(file_path)
    if not file_path_object.absolute().is_file():
        raise Exception(f"File {file_path} is not a file")
    elif not file_path_object.exists():
        raise FileNotFoundError
    file_path = str(file_path_object.absolute())
    filesize = file_path_object.stat().st_size
    file_data = {"file_path": file_path, "file_size": filesize, "buffer_size": BUFFER_SIZE}
    return file_data


def send_file(file_path, transmit_socket, filesize, filename, progress_bar: bool):
    time.sleep(0.2)
    transmit_connection, addr = transmit_socket.accept()
    progress = ""
    if progress_bar:
        progress = tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with transmit_connection:
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    time.sleep(0.2)
                    transmit_connection.send(b"EOF")
                    break
                transmit_connection.send(bytes_read)
                if progress_bar:
                    progress.update(len(bytes_read))
