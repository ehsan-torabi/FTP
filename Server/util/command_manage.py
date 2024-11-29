import asyncio
import os
from socket import socket
import sys

from Server.server import SERVER_PUBLIC_PATH

sys.path.append(os.path.curdir)
from Server.util import help_handler
from Server.util.db_manage import ServerDB
from utils import recive_file


loggedInUsers = []
commandList = ["login", "upload", "download", "mkdir","rmdir", "cd", "resume", "rename", "list","help","quit"]


def command_parser(line: str, conn,addr):
    line_split = line.strip().split(" ")
    command = line_split[0].lower()
    exclude_len_condition = ["help","quit"]
    if len(line_split) <= 1 and command not in exclude_len_condition:
        conn.sendall(f"Please enter full args for {command.upper()} command\n".encode())
        return
    elif command not in commandList:
        conn.sendall("Command not found!\n".encode())
    args = line_split[1:]
    match command:
        case "login":
            asyncio.run(login_handler(args, conn,addr))
        case "upload":
            recive_file.handle_client(conn,SERVER_PUBLIC_PATH)
        case "download":
            pass
        case "mkdir":
            pass
        case "rmdir":
            pass
        case "cd":
            pass
        case "resume":
            pass
        case "rename":
            pass
        case "list":
            pass
        case "help":
            help_handler.show_help(conn)


async def login_handler(args: list, conn:socket,addr):
    global loggedInUsers
    userinfo = str(args[0]).split("@")
    username = userinfo[0]+ ","+str(addr[0])+":"+str(addr[1])
    if username in loggedInUsers:
        conn.sendall("You logged in and now logged out!\n".encode())
        loggedInUsers.remove(username)
        return
    
    elif len(userinfo) < 2:
        conn.sendall(
            "Please enter username and password with correct format:\nusername@password\n".encode()
        )
        return
    else:
        db = ServerDB()
        user_valid = db.validate_user(str(userinfo[0]), str(userinfo[1]))
        if user_valid:
            loggedInUsers.append(username)
            conn.sendall("Login successful.\n".encode())
        else:
            conn.sendall("Username or password incorrect.Please try again!\n".encode())
