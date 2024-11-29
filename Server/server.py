import os
import socket
import threading
from Server.util import command_manage

SERVER_PUBLIC_PATH = os.path.abspath("../Public")

class Server:
    def __init__(self, port) -> None:
        self.port = port

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                sock.bind(("", self.port))
                break
            except OSError:
                self.port += 1

        sock.listen(5)  # Allow up to 5 connections
        print(f"Server running on port {self.port}")
        return sock


def read_connection(conn: socket.socket, addr):
    conn.send("[+] You are connected.\nUse help to see commands.\n".encode())
    print(f"[+] User connected: {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        command_manage.command_parser(data.decode(), conn, addr)


def main():
    with Server(8021).start_server() as srv:
        while True:
            try:
                conn, addr = srv.accept()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue
            t = threading.Thread(target=read_connection, args=(conn, addr))
            t.start()



if __name__ == "__main__":
    main()
