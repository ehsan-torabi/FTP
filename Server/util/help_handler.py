import socket
import os


def show_help(conn: socket.socket):
    os.getcwd()
    with open(os.path.join(os.getcwd(),"util", "assets",  "help.txt"), "r") as f:
        help_content = f.read()
        conn.sendall(help_content.encode("utf-8"))
