import os
import pathlib
import shutil
import socket

from utils import receive_file
from utils import request_parser as rp
from utils.ftp_status_code import FTPStatusCode as FTPStatus
from utils.standard_query import StandardQuery

# Set the current server and local directories
current_server_dir = "."
current_local_dir = os.path.dirname(os.path.abspath(__file__))



def command_parser(user_input, user_socket):
    """Parse and execute user commands."""
    global current_server_dir
    user_command, *args = user_input.split(" ")
    user_command = user_command.lower()
    command_actions = {
        "login": lambda: handle_login(user_socket),
        "upload": lambda: upload_file_handler(user_socket),
        "download": lambda: download_file_handler(user_socket, args),
        "cd": lambda: change_dir_handler(user_socket, args),
        "ldir": lambda: print(current_local_dir),
        "dir": lambda: dir_handler(user_socket, args),
        "rename": lambda: rename_handler(user_socket, args),
        "list": lambda: list_handler(user_socket, args),
        "ls": lambda: list_handler(user_socket, args),
        "lls": lambda: local_list_handler(args),
        "llist": lambda: local_list_handler(args),
        "help": help_handler,
        "quit": lambda: exit_program(user_socket),
        "exit": lambda: exit_program(user_socket),
        "mkdir": lambda: make_dir_handler(user_socket, args),
        "rmdir": lambda: remove_dir_handler(user_socket, args),
        "rm": lambda: remove_file_handler(user_socket, args),
        "resume": lambda: resume_download_handler(user_socket, args),
    }

    command_actions.get(user_command, lambda: print("Unknown command."))()


def handle_login(user_socket):
    """Handle user login."""
    pass

def upload_file_handler(user_socket):
    pass

def download_file_handler(user_socket, args):
    StandardQuery(auth_token="1234", command="download", command_args=args,
                  current_dir=current_server_dir).serialize_and_send(user_socket)
    response = rp.response_parser(user_socket.recv(4096))
    if response["accept"]:
        transmit_port = int(response["data"]["transmit_port"])
        filename = os.path.basename(response["data"]["file_path"])
        filesize = int(response["data"]["file_size"])
        transmit_buffer_size = int(response["data"]["buffer_size"])
        checksum = response["data"]["checksum"]
        transmit_result = receive_file.retrieve_file(user_socket, current_local_dir, transmit_port, filename, filesize,
                                                     transmit_buffer_size,checksum, True)
        if transmit_result:
            print("File downloaded successfully")
    else:
        handle_error(response)



def list_handler(user_socket: socket.socket, args):
    """List files in the current server directory."""
    terminal_width = shutil.get_terminal_size().columns
    query = StandardQuery("1234", "list", current_server_dir, command_args=args,
                          data={"terminal_width": terminal_width})
    query.serialize_and_send(user_socket)
    print("Server dir list:\n")
    handle_response(user_socket, '')


def local_list_handler(args:list[str]):
    dir_path = os.path.abspath(current_local_dir)
    if args:
         dir_path =  os.path.abspath(os.path.join(current_local_dir, args[0]))
    if args and args[0] == "..":
        dir_path = str(pathlib.Path(current_local_dir).parent)

    ls = os.listdir(dir_path)
    ls.sort()
    terminal_width = shutil.get_terminal_size().columns
    max_length = max(len(name) for name in ls) if ls else 0
    num_columns = max(1, terminal_width // (max_length + 2))

    body = ""
    for i, obj in enumerate(ls):
        body += f"{obj:<{max_length}}  "
        if (i + 1) % num_columns == 0:
            body += "\n"

    if len(ls) % num_columns != 0:
        body += "\n"
    print("Local dir list:\n")
    print(body)


def change_dir_handler(user_socket, args):
    """Change the current server directory."""
    global current_server_dir
    query = StandardQuery("1234", "cd", current_server_dir, command_args=args)
    query.serialize_and_send(user_socket)
    response = rp.response_parser(user_socket.recv(4096))
    if response["accept"]:
        current_server_dir = response["data"]["current_directory"]
        print("Changed directory successfully.")
    else:
        handle_error(response)


def dir_handler(user_socket, args):
    """Display the current directory path."""
    query = StandardQuery("1234", "dir", current_server_dir, command_args=args)
    query.serialize_and_send(user_socket)
    handle_response(user_socket, "directory_path")


def rename_handler(user_socket, args):
    """Rename a file on the server."""
    query = StandardQuery("1234", "rename", current_server_dir, command_args=args)
    query.serialize_and_send(user_socket)
    response = rp.response_parser(user_socket.recv(4096))
    if response["accept"]:
        print("Renamed successfully.")
    else:
        handle_error(response)


def handle_response(user_socket, field: str):
    """Handle the server's response to a command."""
    raw_response = user_socket.recv(4096)
    if raw_response:
        response = rp.response_parser(raw_response)
        if response["accept"]:
            if field:
                print(response["data"][field])
            else:
                print(response["data"])
        else:
            handle_error(response)
    else:
        print("Failed to get response. Check your connection.")


def make_dir_handler(user_socket, args):
    """Make a directory on the server."""
    query = StandardQuery("1234", "mkdir", current_server_dir, command_args=args)
    query.serialize_and_send(user_socket)
    response = rp.response_parser(user_socket.recv(4096))
    if response["accept"]:
        print("Renamed successfully.")
    else:
        handle_error(response)


def remove_dir_handler(user_socket, args):
    pass


def remove_file_handler(user_socket, args):
    pass


def resume_download_handler(user_socket, args):
    pass


def handle_error(response):
    """Handle errors based on the server's response status code."""
    status_code = response["status_code"]
    error_messages = {
        FTPStatus.PATH_NOT_DIRECTORY: "Path is not a directory.",
        FTPStatus.FILE_UNAVAILABLE: "File not found in this directory.",
        FTPStatus.PERMISSION_DENIED: "Permission denied.",
        FTPStatus.SYNTAX_ERROR_IN_PARAMETERS: "Syntax error.",
        FTPStatus.FILE_EXISTS_ERROR: "File exists.",
        FTPStatus.LOCAL_ERROR_IN_PROCESSING: "Unknown error.",
    }
    print(error_messages.get(status_code, "An unknown error occurred."))
    if "data" in response:
        print(response["data"])


def help_handler():
    """Display help information."""
    file_path = os.path.abspath("/home/ehsan/Workspace/FTP/help.txt")
    try:
        with open(file_path, "rt") as f:
            help_content = f.read()
            print(help_content)
    except FileNotFoundError:
        print("Help file not found.")


def exit_program(user_socket):
    """Close the user socket and exit the program."""
    user_socket.close()
    print("Connection closed. Exiting the program.")
    exit(0)
