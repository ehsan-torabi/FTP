import os
import time

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def receive_file(conn,file_path):
    # receive the file infos
    # receive using client socket, not server socket
    received = str(conn.recv(BUFFER_SIZE))
    time.sleep(0.2)
    print(str(received))
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename).replace("b'","")
    filesize = int(filesize.replace("'",""))
    with open(os.path.join(file_path,filename), "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = conn.recv(BUFFER_SIZE)
            if bytes_read == b"EOF":
                # file transmitting is done
                conn.send("File send Successfully.\n".encode())
                break
            # write to the file the bytes we just received
            f.write(bytes_read)

def handle_client(conn,file_path):
  receive_file(conn,file_path)