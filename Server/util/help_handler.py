import socket


def show_help(conn:socket.socket):
    with open("Server/util/assets/help.md","r") as f:
        help_contetnt = f.read()
        conn.sendall(help_contetnt.encode("utf-8"))