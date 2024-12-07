import os
from shutil import rmtree
from socket import socket

from Server.server import SERVER_START_PATH
from Server.util.db_manage import ServerDB
from utils import receive_file, send_file
from utils import request_parser as rp
from utils.command_codes import code_command_dict
from utils.ftp_status_code import FTPStatusCode as FTPSTATUS
from utils.path_tools import process_path, validate_path
from utils.send_file import get_file_info, create_transmit_socket
from utils.standard_response import StandardResponse
from Server.util.logging_config import server_logger

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
    user_request = rp.request_parser(data)

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


def command_parser(data, conn, addr):
    """Parse and execute the command received from the user."""
    server_logger.info(f"Received command from {addr}")
    command, args, user_current_directory, data = user_request_process(data, conn)
    if not command:
        server_logger.warning(f"Invalid command received from {addr}")
        return
    try:
        command_handlers = {
            "login": lambda: login_handler(args, conn, addr),
            "upload": lambda: upload_handler(args, data, user_current_directory, conn),
            "download": lambda: download_handler(args, user_current_directory, conn),
            "cd": lambda: change_dir_handler(args, user_current_directory, conn),
            "pwd": lambda: handle_dir_command(user_current_directory, conn),
            "rename": lambda: rename_handler(args, user_current_directory, conn),
            "list": lambda: list_handler(args, user_current_directory, data, conn),
            "ls": lambda: list_handler(args, user_current_directory, data, conn),
            "mkdir": lambda: mkdir_handler(args, user_current_directory, conn),
            "rmdir": lambda: rmdir_handler(args, user_current_directory,data, conn),
            "rm": lambda:remove_file_handler(args, user_current_directory, conn),
            "resume": lambda:
            "pass",
        }

        handler = command_handlers.get(command, lambda: send_command_not_implemented(conn))
        server_logger.info(f"Executing command: {command} for {addr}")
        handler()
    except Exception as e:
        server_logger.exception(f"Error processing command {command} from {addr}: {e}")
        send_command_not_implemented(conn)


def send_command_not_implemented(conn):
    """Send a command not implemented response to the client."""
    StandardResponse(accept=False, status_code=FTPSTATUS.COMMAND_NOT_IMPLEMENTED).serialize_and_send(conn)


def send_syntax_error(conn):
    """Send a syntax error response to the client."""
    StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)


def download_handler(args, user_current_directory, conn):
    """Handle the download request."""
    try:
        dir_path = process_path(args["0"],user_current_directory)
        file_data = get_file_info(dir_path)
        transmit_socket, port = create_transmit_socket()
        file_data["transmit_port"] = port
        file_name = os.path.basename(file_data["file_path"])
        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK, data=file_data).serialize_and_send(conn)
        send_file.send_file(dir_path, transmit_socket, file_data["file_size"], file_name, False)
        transmit_socket.close()
    except PermissionError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except Exception as e:
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)


def upload_handler(args, data, user_current_directory, conn):
    """Handle the upload request"""
    file_name=""
    try:
        dir_path = user_current_directory
        if len(args) > 1:
            dir_path = process_path(args["1"],user_current_directory)
            if not validate_path(dir_path,dir_check=True):
                raise NotADirectoryError


        file_name = os.path.basename(data["file_path"])
        server_logger.info(f"Upload request for file: {file_name} to directory: {dir_path}")

        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK).serialize_and_send(conn)

        rec_result = receive_file.retrieve_file(
            dir_path,
            data["transmit_port"],
            file_name,
            data["file_size"],
            data["buffer_size"],
            data["checksum"],
            False
        )

        if rec_result:
            server_logger.info(f"Successful upload of file: {file_name}")
            StandardResponse(accept=True, status_code=FTPSTATUS.REQUESTED_FILE_ACTION_OK).serialize_and_send(conn)
        else:
            server_logger.warning(f"Failed upload of file: {file_name}")
            StandardResponse(accept=False,
                             status_code=FTPSTATUS.REQUESTED_ACTION_NOT_TAKEN_FILE_UNAVAILABLE).serialize_and_send(conn)

    except PermissionError:
        server_logger.error(f"Permission denied for file upload: {file_name}")
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        server_logger.error("Invalid upload parameters")
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except FileNotFoundError :
        server_logger.error(f"File not found during upload: {file_name}")
        StandardResponse(accept=False, status_code=FTPSTATUS.FILE_UNAVAILABLE).serialize_and_send(conn)
    except NotADirectoryError:
        server_logger.error(f"Directory not found during upload: {file_name}")
        StandardResponse(accept=False,status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)
    except Exception as e:
        server_logger.exception(f"Unexpected error during file upload: {e}")
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)


def rmdir_handler(args, user_current_directory,data, conn):
    """Remove a directory."""
    try:
        dir_path = process_path(args["0"], user_current_directory)
        if not validate_path(dir_path, dir_check=True):
            raise NotADirectoryError
        if data["method"] == "n":
            os.rmdir(dir_path)
        elif data["method"] == "r":
            rmtree(dir_path)
        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK).serialize_and_send(conn)
    except PermissionError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except NotADirectoryError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)
    except Exception as e:
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)


def remove_file_handler(args, user_current_directory, conn):
    """Remove a directory."""
    try:
        file_path = process_path(args["0"], user_current_directory)
        if not validate_path(file_path, file_check=True):
            raise FileNotFoundError
        os.remove(file_path)
        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK).serialize_and_send(conn)
    except PermissionError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except FileNotFoundError:
        StandardResponse(accept=False, status_code=FTPSTATUS.FILE_UNAVAILABLE).serialize_and_send(conn)
    except Exception as e:
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)


def handle_dir_command(user_current_directory, conn):
    """Handle the 'dir' command and send the current directory path."""
    data = {"directory_path": os.path.abspath(user_current_directory)}
    StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK, data=data).serialize_and_send(conn)


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

    dir_path = process_path(args["0"],user_current_dir )
    user_terminal_width = request_data["terminal_width"]

    if not os.path.isdir(dir_path):
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)
        return

    ls = os.listdir(dir_path)
    ls.sort()
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


def mkdir_handler(args, user_current_directory, conn):
    """Make a directory."""
    try:

        if len(args["0"]) > 1:
            dirs = str(args["0"]).strip().split("/")
            new_dir = user_current_directory
            for dir in dirs:
                if dir not in [os.path.dirname(user_current_directory),os.path.basename(user_current_directory)]:
                    new_dir = os.path.join(new_dir, dir)
                    dir_path = process_path(new_dir,user_current_directory)
                    os.mkdir(dir_path)

        else:
            dir_path = process_path(args["0"], user_current_directory)
            os.mkdir(dir_path)
        StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK).serialize_and_send(conn)
    except PermissionError:
        StandardResponse(accept=False, status_code=FTPSTATUS.PERMISSION_DENIED).serialize_and_send(conn)
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
    except FileExistsError:
        StandardResponse(accept=False, status_code=FTPSTATUS.FILE_EXISTS_ERROR).serialize_and_send(conn)
    except Exception as e:
        StandardResponse(accept=False, status_code=FTPSTATUS.LOCAL_ERROR_IN_PROCESSING, data=str(e)).serialize_and_send(
            conn)


def change_dir_handler(args: dict[str: str], user_current_dir: str, conn: socket):
    """Change the current directory to the specified path."""
    if not args:
        args = {"0": user_current_dir}

    dir_path = process_path(args["0"], user_current_dir)

    if os.path.isdir(dir_path):
        StandardResponse(accept=True, status_code=FTPSTATUS.CHANGE_DIRECTORY_ACCEPTED,
                         data={"current_directory": dir_path}).serialize_and_send(conn)
    else:
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)


def rename_handler(args: dict[str: str], user_current_dir: str, conn: socket):
    """Rename a file or directory."""
    try:
        old_dir_path = process_path(args["0"],user_current_dir)
        new_dir_path = process_path(args["1"],user_current_dir)
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
