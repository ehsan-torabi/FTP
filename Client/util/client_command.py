import os
import sys

from Client.util.help_handler import show_help
from Client.util.standardquery import StandardQuery
import pathlib
sys.path.append('.')
from utils.ftp_status_code import FTPStatusCode as FTPStatus
from utils.ftp_status_code import get_ftp_status_message
from utils import request_parser as rp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import send_file, receive_file, ftp_status_code

current_dir = os.path.dirname(os.path.abspath(__file__))


def command_parser(user_input, user_socket):
    global current_dir
    user_command = user_input.lower().split(" ")[0]
    args = user_input.lower().split(" ")[1:]
    match user_command:
        case "login":
            response = rp.server_response_parser(user_socket.recv(1024))
            print(get_ftp_status_message(int(response)))
        case "upload":
            send_file.upload_file(user_socket, args[0])
        case "download":
            receive_file.download_file(user_socket)
        case "mkdir":
            pass
        case "rmdir":
            pass
        case "rm":
            pass
        case "cd":
            change_dir_handler(user_socket,user_command,args)
        case "dir":
            StandardQuery("1234", user_command, current_dir, command_args=args).serialize_and_send(user_socket)
            response = rp.server_response_parser(user_socket.recv(1024))
            print(response["data"]["directory_path"])
        case "resume":
            pass
        case "rename":
            pass
        case "list" | "ls":
            list_handler(user_socket,user_command,args)
        case "help":
            show_help()
        case "quit" | "exit":
            user_socket.close()
            exit(0)


def list_handler(user_socket,user_command,args):
    StandardQuery("1234", user_command, current_dir, command_args=args).serialize_and_send(user_socket)
    response = rp.server_response_parser(user_socket.recv(4096))
    if response["accept"]:
        print(response["data"])
    elif response["status_code"] == FTPStatus.PATH_NOT_DIRECTORY:
        print("Path is not directory.")
    else:
        print("Failed to get directory list.")

def change_dir_handler(user_socket,user_command,args):
    global current_dir
    StandardQuery("1234", user_command, current_dir, command_args=args).serialize_and_send(user_socket)
    response = rp.server_response_parser(user_socket.recv(1024))
    if response["accept"]:
        if response["status_code"] == FTPStatus.CHANGE_DIRECTORY_ACCEPTED:
            current_dir = response["data"]["current_directory"]
            print("Change directory successfully.")
    elif response["status_code"] == FTPStatus.PATH_NOT_DIRECTORY:
        print("Path is not directory.")
    else:
        print("Failed to change directory")