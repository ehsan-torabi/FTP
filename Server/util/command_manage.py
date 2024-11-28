import asyncio
from socket import socket
from Server.util.db_manage import ServerDB


loggedInUsers = []
commandList = ["login", "upload", "download", "mkdir","rmdir", "cd", "resume", "rename", "list"]


def command_parser(line: str, conn,addr):
    line_splited = line.strip().split(" ")
    command = line_splited[0].lower()
    if len(line_splited) <= 1:
        conn.sendall(f"Plese enter full args for {command.upper()} command\n".encode())
        return
    elif command not in commandList:
        conn.sendall("Command not found!\n".encode())
    args = line_splited[1:]
    # print(f"command: {command}\targs:{args}")
    match command:
        case "login":
            asyncio.run(login_handler(args, conn,addr))
        case "upload":
            pass
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
            pass


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
            "Plesae enter username and password with correct format:\nusername@password\n".encode()
        )
        return
    else:
        db = ServerDB()
        userValid = await db.validate_user(userinfo[0], userinfo[1])
        if userValid:
            loggedInUsers.append(username)
            conn.sendall("Login succesful.\n".encode())
        else:
            conn.sendall("Username or password incorrect.Please try again!\n".encode())
