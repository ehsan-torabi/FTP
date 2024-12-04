import os
import shutil
import socket

from Client.util.standardquery import StandardQuery
from utils import request_parser as rp
from utils import send_file, receive_file
from utils.ftp_status_code import FTPStatusCode as FTPStatus

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
        "upload": lambda: send_file.upload_file(user_socket, args[0]),
        "download": lambda: receive_file.download_file(user_socket),
        "cd": lambda: change_dir_handler(user_socket, args),
        "cwd": lambda: print(current_local_dir),
        "dir": lambda: dir_handler(user_socket, args),
        "rename": lambda: rename_handler(user_socket, args),
        "list": lambda: list_handler(user_socket, args),
        "ls": lambda: list_handler(user_socket, args),
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


def list_handler(user_socket: socket.socket, args):
    """List files in the current server directory."""
    terminal_width = shutil.get_terminal_size().columns
    query = StandardQuery("1234", "list", current_server_dir, command_args=args,
                          data={"terminal_width": terminal_width})
    query.serialize_and_send(user_socket)
    handle_response(user_socket, '')


def change_dir_handler(user_socket, args):
    """Change the current server directory."""
    global current_server_dir
    query = StandardQuery("1234", "cd", current_server_dir, command_args=args)
    query.serialize_and_send(user_socket)
    response = rp.server_response_parser(user_socket.recv(4096))
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
    response = rp.server_response_parser(user_socket.recv(4096))
    if response["accept"]:
        print("Renamed successfully.")
    else:
        handle_error(response)


def handle_response(user_socket, field: str):
    """Handle the server's response to a command."""
    raw_response = user_socket.recv(4096)
    if raw_response:
        response = rp.server_response_parser(raw_response)
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
    response = rp.server_response_parser(user_socket.recv(4096))
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
    file_path = os.path.abspath("help.txt")
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
