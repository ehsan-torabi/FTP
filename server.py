import os
import sys
sys.path.append(os.path.dirname(__file__))
import socket
import threading

from Server.util.server_command import command_parser
from Server.util.logging_config import server_logger




class Server:
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.bind_socket()
        self.sock.listen(5)  # Allow up to 5 connections
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_logger.info(f"Server running on port {self.port}")

    def bind_socket(self):
        while True:
            try:
                self.sock.bind(("127.0.0.1", self.port))
                break
            except OSError:
                self.port += 1

    def accept_connections(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                threading.Thread(target=self.handle_connection, args=(conn, addr)).start()
            except KeyboardInterrupt:
                server_logger.info("Server stopped.")
                self.shutdown()
                break
            except Exception as e:
                server_logger.info(f"Error accepting connection: {e}")

    def handle_connection(self, conn: socket.socket, addr):
        server_logger.info(f"[+] User connected: {addr}")
        with conn:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    command_parser(data, conn, addr)
                except ConnectionResetError:
                    server_logger.info(f"[-] Connection reset by {addr}")
                    break
                except Exception as e:
                    server_logger.info(f"Error handling connection from {addr}: {e}")
                    break

    def shutdown(self):
        self.sock.close()


def main(port=8021):
    server = Server(port)
    server.start()
    server.accept_connections()


if __name__ == "__main__":
    if len(sys.argv) == 2:
         main(int(sys.argv[1]))
    else:
        main()