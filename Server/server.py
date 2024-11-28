import asyncio
import os
import threading
import socket
import sys
sys.path.append(os.path.curdir)
from Server.util import command_manage


class server:
    def __init__(self, port) -> None:
        self.port = port

    def startServer(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.port += 1
                sock.bind(("", self.port))
                break
            except OSError:
                continue
        
        sock.listen(0)
        print(f"Server run on {self.port}")
        return sock


def readConnection(conn:socket.socket,addr):
    while True:
        data = conn.recv(2048)
        if data.decode().strip().lower() == "quit":
            conn.close()
            break
        command_manage.command_parser(data.decode(),conn,addr)

def main():
    with server(8021).startServer() as srv:
        while True:
            try:
                conn, addr = srv.accept()
            except:
                continue
            threading.Thread(target=readConnection,args=(conn,addr),daemon=False).start() 
            


if __name__ == "__main__":
    asyncio.run(main())
