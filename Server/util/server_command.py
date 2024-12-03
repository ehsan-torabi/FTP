import os
import pathlib
import sys
import time
from socket import socket

from Server.server import SERVER_START_PATH
from Server.util.standard_response import StandardResponse
from utils import request_parser as rp
from utils.command_codes import code_command_dict
from utils.ftp_status_code import FTPStatusCode as FTPSTATUS

sys.path.append(os.path.curdir)
from Server.util.db_manage import ServerDB
from utils import receive_file, send_file

loggedInUsers = []
command_list = ["login", "upload", "download", "mkdir", "rmdir",
                "cd", "resume", "rename", "list", "help", "quit",
                "exit", "dir", "ls", "rm"]

os.chdir(SERVER_START_PATH)


def user_request_process(data, conn):
    user_request = rp.client_response_parser(data)
    command = user_request["command"]
    try:
        command = code_command_dict[command]
    except KeyError:
        StandardResponse(accept=False, status_code=FTPSTATUS.COMMAND_NOT_IMPLEMENTED).serialize_and_send(conn)
    args = user_request["command_args"]
    user_current_directory = user_request["current_dir"]
    if command not in command_list:
        StandardResponse(accept=False, status_code=FTPSTATUS.COMMAND_NOT_IMPLEMENTED).serialize_and_send(conn)
        return None,None,None
    if not user_current_directory:
        StandardResponse(accept=False, status_code=FTPSTATUS.SYNTAX_ERROR_IN_PARAMETERS).serialize_and_send(conn)
        return None,None,None
    return command,args,user_current_directory

def command_parser(data, conn, addr):
    command,args,user_current_directory = user_request_process(data, conn)
    if not command:
        return
    match command:
        case "login":
            login_handler(args, conn, addr)
        case "upload":
            receive_file.download_file(conn, SERVER_START_PATH)
        case "download":
            send_file.upload_file(conn, args[0])
        case "mkdir":
            pass
        case "rmdir":
            pass
        case "rm":
            pass
        case "cd":
            change_dir_handler(args, user_current_directory,conn)
        case "dir":
            data = {"directory_path": os.path.abspath(user_current_directory)}
            StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK,data=data).serialize_and_send(conn)
        case "resume":
            pass
        case "rename":
            pass
        case "list" | "ls":
            list_handler(args, user_current_directory,conn)
        case _:
            StandardResponse(accept=False,
                                        status_code=FTPSTATUS.SYNTAX_ERROR_COMMAND_UNRECOGNIZED).serialize_and_send(conn)


def login_handler(args: list, conn: socket, addr):
    global loggedInUsers
    username = ""
    userinfo = []
    try:
        userinfo = str(args[0]).split("@")
        if len(userinfo) != 2:
            raise IndexError
        username = userinfo[0] + "," + str(addr[0]) + ":" + str(addr[1])
    except IndexError:
        conn.send(
            f"{FTPSTATUS.SYNTAX_ERROR_COMMAND_UNRECOGNIZED}".encode("utf-8")
        )
        return
    if username in loggedInUsers:
        conn.send(f"{FTPSTATUS.USER_LOGGED_IN}".encode("utf-8"))
        return

    else:
        db = ServerDB()
        user_valid = db.validate_user(str(userinfo[0]), str(userinfo[1]))
        if user_valid:
            loggedInUsers.append(username)
            conn.send(f"{FTPSTATUS.USER_LOGGED_IN}".encode("utf-8"))
        else:
            conn.send(f"{FTPSTATUS.NOT_LOGGED_IN}".encode("utf-8"))


def list_handler(args: dict[str:str],user_current_dir:str, conn: socket):
    dir_path = os.path.abspath(user_current_dir)
    if len(args) != 0:
        dir_path = os.path.abspath(os.path.join(user_current_dir,args["0"]))
        if args["0"] == "..":
            dir_path = str(pathlib.Path(user_current_dir).parent)

    if not os.path.isdir(dir_path):
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)

        return
    ls = os.listdir(dir_path)
    body = ""
    for num, obj in enumerate(ls, start=1):
        body += f"{obj:30s}\t"
        if num % 6 == 0:
            body += "\n"
    StandardResponse(accept=True, status_code=FTPSTATUS.COMMAND_OK,data=body).serialize_and_send(conn)


def change_dir_handler(args: dict[str:str],user_current_dir:str, conn: socket):
    dir_path = os.path.abspath(user_current_dir)
    if len(args) >= 1:
        dir_path = os.path.abspath(os.path.join(user_current_dir,args["0"]))
        if args["0"] == "..":
            dir_path = str(pathlib.Path(user_current_dir).parent)

    if os.path.isdir(dir_path):
        StandardResponse(accept=True, status_code=FTPSTATUS.CHANGE_DIRECTORY_ACCEPTED,data={"current_directory":dir_path}).serialize_and_send(conn)

    else:
        StandardResponse(accept=False, status_code=FTPSTATUS.PATH_NOT_DIRECTORY).serialize_and_send(conn)
