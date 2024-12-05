import hashlib
import os
import socket

from tqdm import tqdm

BUFFER_SIZE = 4096
GENERAL_DOWNLOAD_DIR = SERVER_PUBLIC_PATH = os.path.abspath("../Downloads")
os.makedirs(GENERAL_DOWNLOAD_DIR, exist_ok=True)


def retrieve_file(file_path:GENERAL_DOWNLOAD_DIR, transmit_port, file_name, file_size, buffer_size,
                  checksum, progress_bar):
    try:
        progress = ""
        if progress_bar:
            progress = tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
        transmit_socket = socket.create_connection(("localhost", transmit_port))
        with transmit_socket:
            with open(os.path.join(file_path, file_name), "wb") as f:
                while True:
                    bytes_read = transmit_socket.recv(buffer_size)
                    if bytes_read == b"EOF" or not bytes_read:
                        if progress_bar:
                            progress.close()
                        break
                    if bytes_read[-3:] == b"EOF":
                        f.write(bytes_read[:-3])
                        if progress_bar:
                            progress.close()
                        break
                    f.write(bytes_read)
                    if progress_bar:
                        progress.update(len(bytes_read))
            with open(os.path.join(file_path, file_name), "rb") as file:
                new_checksum = hashlib.file_digest(file, "md5").hexdigest()
                print(new_checksum)
                if checksum == new_checksum:
                    return True
        return False


    except Exception as e:
        print(f"Error in receive file: {e}")
        return False
