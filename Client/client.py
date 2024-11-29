import socket as s
import threading as thr
from utils import send_file

def get_data(usr_socket):
    while True:
        data = usr_socket.recv(1024)
        if not data:
            break
        print(data.decode(), end="")

def send_data(usr_socket):
    while True:
        user_input = input()
        args = user_input.split(" ")[1:]
        usr_socket.sendall(user_input.encode())
        if user_input.lower().startswith("upload"):
            send_file.upload_file(usr_socket, args[0])
        if user_input.lower().startswith("quit"):
            usr_socket.shutdown(0)
            return

port = input("Enter Port: ")
with s.socket(s.AF_INET, s.SOCK_STREAM) as soc:
    soc.connect(('', int(port)))
    t1 = thr.Thread(target=get_data, args=(soc,))
    t2 = thr.Thread(target=send_data, args=(soc,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
