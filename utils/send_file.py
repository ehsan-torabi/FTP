import os
import time
from tqdm import tqdm


SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def send_file(file_path,conn):
    file_path_object = os.path.abspath(file_path)
    filename = os.path.basename(file_path_object)
    filesize = os.path.getsize(file_path_object)

    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
    time.sleep(0.2)
    # start sending the file
    progress = tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(file_path_object, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                time.sleep(0.2)
                conn.send(b"EOF")
                break
            # we use sendall to assure transimission in
            # busy networks
            conn.sendall(bytes_read)
            # update the progress bar

            progress.update(len(bytes_read))



def upload_file(conn, file_path):
  send_file(file_path, conn)