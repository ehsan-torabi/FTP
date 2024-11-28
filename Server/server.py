import asyncio
import threading
import socket


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


def readConnection(con:socket.socket):
    while True:
        data = con.recv(2048)
        if data.decode().strip().lower() == "quit":
            con.close()
            break
        con.sendall("OK".encode())

def main():
    with server(8021).startServer() as srv:
        while True:
            try:
                con, addr = srv.accept()
            except:
                continue
            threading.Thread(target=readConnection,args=(con,),daemon=False).start() 
            




if __name__ == "__main__":
    asyncio.run(main())
