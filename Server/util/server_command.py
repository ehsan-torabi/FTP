import os
import pathlib
from socket import socket

from Server.server import SERVER_START_PATH
from Server.util.db_manage import ServerDB
from Server.util.standard_response import StandardResponse
from utils import receive_file, send_file
from utils import request_parser as rp
from utils.command_codes import code_command_dict
from utils.ftp_status_code import FTPStatusCode as FTPSTATUS

# Global variables
loggedInUsers = []
command_list = [
    "login", "upload", "download", "mkdir", "rmdir",
    "cd", "resume", "rename", "list", "help.txt", "quit",
    "exit", "dir", "ls", "rm"
]

# Change the current working directory to the server start path
os.chdir(SERVER_START_PATH)


def user_request_process(data, conn):
    """Process the user request and return command, arguments, and current directory."""
    user_request = rp.client_response_parser(data)
    print(user_request)

    command = code_command_dict.get(user_request["command"])
    if command is None:
        send_command_not_implemented(conn)
        return None, None, None, None

    args = user_request["command_args"]
    user_current_directory = user_request["current_dir"]
    data = user_request["data"]

    if not user_current_directory:
        send_syntax_error(conn)
        return None, None, None, None

    return command, args, user_current_directory, data


def send_command_not_implemented(conn):
    """Send a command not implemented response to the client."""
    StandardResponse(accept=False, status_code=FTPSTATUS.COMMAND_NOT_IMPLEMENTED).serialize_and_send(conn)


def send_syntax_error(conn):
    """Send a syntax error response to the client."""
    StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)


def command_parser(data, conn, addr):
    """Parse and execute the command received from the user."""
    command, args, user_current_directory, data = user_request_process(data, conn)
    if not command:
        return

    command_handlers = {
        "login": lambda: login_handler(args, conn, addr),
        "upload": lambda: receive_file.download_file(conn, SERVER_START_PATH),
        "download": lambda: send_file.upload_file(conn, args[0]),
        "cd": lambda: change_dir_handler(args, user_current_directory, conn),
        "dir": lambda: handle_dir_command(user_current_directory, conn),
        "rename": lambda: rename_handler(args, user_current_directory, conn),
        "list": lambda: list_handler(args, user_current_directory, data, conn),
        "ls": lambda: list_handler(args, user_current_directory, data, conn),
        # Add placeholders for unimplemented commands
        "mkdir": lambda:
        "pass",
        "rmdir": lambda:
        "pass",
        "rm": lambda:
        "pass",
        "resume": lambda:
        "pass",
    }

    handler = command_handlers.get(command, lambda: send_command_not_implemented(conn))
    handler()


def handle_dir_command(user_current_directory, conn):
    """Handle the 'dir' command and send the current directory path."""
    data = {"directory_path": os.path.abspath(user_current_directory)}
    StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK, data=data).serialize_and_send(conn)


def address_process(user_current_dir: str, arg: str):
    """Process the address based on the current directory and argument."""
    dir_path = os.path.abspath(user_current_dir)
    if arg:
        return os.path.abspath(os.path.join(user_current_dir, arg))
    if arg == "..":
        return str(pathlib.Path(user_current_dir).parent)
    return dir_path


def login_handler(args: list, conn: socket, addr):
    """Handle user login."""
    global loggedInUsers
    try:
        username = f"{args[0].split('@')[0]},{addr[0]}:{addr[1]}"
        if username in loggedInUsers:
            conn.send(f"{FTPSTATUS.USER_LOGGED_IN}".encode("utf-8"))
            return

        db = ServerDB()
        user_valid = db.validate_user(args[0].split('@')[0], args[0].split('@')[1])
        if user_valid:
            loggedInUsers.append(username)
            conn.send(f"{FTPSTATUS.USER_LOGGED_IN}".encode("utf-8"))
        else:
            conn.send(f"{FTPSTATUS.NOT_LOGGED_IN}".encode("utf-8"))
    except IndexError:
        conn.send(f"{FTPSTATUS.SYNTAX_ERROR_COMMAND_UNRECOGNIZED}".encode("utf-8"))


def list_handler(args: dict[str: str], user_current_dir: str, request_data, conn: socket):
    """List files in the specified directory."""
    if not args:
        args = {"0": user_current_dir}

    dir_path = address_process(user_current_dir, args["0"])
    user_terminal_width = request_data["terminal_width"]

    if not os.path.isdir(dir_path):
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)
        return

    ls = os.listdir(dir_path)
    terminal_width = user_terminal_width
    max_length = max(len(name) for name in ls) if ls else 0
    num_columns = max(1, terminal_width // (max_length + 2))

    body = ""
    for i, obj in enumerate(ls):
        body += f"{obj:<{max_length}}  "
        if (i + 1) % num_columns == 0:
            body += "\n"

    if len(ls) % num_columns != 0:
        body += "\n"

    StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK, data=body).serialize_and_send(conn)


def change_dir_handler(args: dict[str: str], user_current_dir: str, conn: socket):
    """Change the current directory to the specified path."""
    if not args:
        args = {"0": user_current_dir}

    dir_path = address_process(user_current_dir, args["0"])

    if os.path.isdir(dir_path):
        StandardResponse(accept=True, status_code=FTPSTATUS.CHANGE_DIRECTORY_ACCEPTED,
                         data={"current_directory": dir_path}).serialize_and_send(conn)
    else:
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)


def rename_handler(args: dict[str: str], user_current_dir: str, conn: socket):
    """Rename a file or directory."""
    try:
        old_dir_path = address_process(user_current_dir, args["0"])
        new_dir_path = address_process(user_current_dir, args["1"])
        os.rename(old_dir_path, new_dir_path)
        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK).serialize_and_send(conn)
    except FileNotFoundError:
        StandardResponse(accept=False, status_code=FTPSTATUS.FILE_UNAVAILABLE).serialize_and_send(conn)
    except PermissionError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except FileExistsError:
        StandardResponse(accept=False, status_code=FTPSTATUS.FILE_EXISTS_ERROR).serialize_and_send(conn)
    except Exception as e:
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)
