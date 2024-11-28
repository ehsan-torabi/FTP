import socket as s
import threading as thr

op_lock = thr.Lock()

def getData(soc): 
    while True:
        op_lock.acquire()
        data = soc.recv(1024)
        if data:
            print(data.decode(),end="")


def sendData(soc):
    while True:
        soc.sendall(input().encode())
        op_lock.release()

port = input("Enter Port: ")
with s.socket(s.AF_INET,s.SOCK_STREAM) as soc:
    soc.connect(('',int(port)))
    t1 = thr.Thread(target=getData,args=(soc,))
    t2 = thr.Thread(target=sendData,args=(soc,))
    t1.start()
    t2.start()
    t1.join()
    t2.join
        
