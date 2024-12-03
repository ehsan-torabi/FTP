import os
import socket as s
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Client.util.client_command import command_parser


def start_cycle(usr_socket):
    while True:
        try:
            user_input = input("ftp> ")
            command_parser(user_input, usr_socket)
        except TimeoutError:
            print("Timeout Error\nCheck your connection")


port = input("Enter Port: ")
try:
    with s.socket(s.AF_INET, s.SOCK_STREAM) as soc:
        soc.connect(('', int(port)))
        # soc.settimeout(1)
        print("[+] You are connected.\nUse 'help' to see commands.")
        start_cycle(soc)
except KeyboardInterrupt:
    print("\nPlease use 'exit' or 'quit' to quit.")
