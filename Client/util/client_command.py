import cmd
import getpass
import os
import shutil
import sys

from utils import receive_file, send_file
from utils import request_parser as rp
from utils.auth import authorize
from utils.ftp_status_code import FTPStatusCode as FTPStatus
from utils.path_tools import process_path, validate_path
from utils.send_file import get_file_info, create_transmit_socket
from utils.standard_query import StandardQuery


current_local_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def login_handler(user_socket)-> (str,str):
    username = input("username: ")
    password = getpass.getpass()
    data = authorize(username, password, user_socket)
    if data:
        auth_token = data['auth_token']
        access_path = data['access_path']
        print("You are logged in.")
        return auth_token, access_path
    else:
        print("Username or password is incorrect.")
        return None, None


class FTPClient(cmd.Cmd):
    intro = 'Welcome to the FTP client. Type help or ? to list commands.'
    prompt = '(ftp) '

    def __init__(self, user_socket):
        super().__init__()
        self.user_socket = user_socket
        auth_token, access_path = login_handler(self.user_socket)
        self.auth_token = auth_token
        self.access_path = access_path
    def do_login(self, arg):
        """Handle user login."""
        auth_token, access_path = login_handler(self.user_socket)
        self.auth_token = auth_token
        self.access_path = access_path

    def do_upload(self, arg):
        """Upload a file to the server."""
        args = arg.split()
        self.upload_file_handler(args)

    def do_download(self, arg):
        """Download a file from the server."""
        args = arg.split()
        self.download_file_handler(args)

    def do_cd(self, arg):
        """Change the current server directory."""
        args = arg.split()
        self.change_dir_handler(args)

    def do_lpwd(self, arg):
        """Print current local directory."""
        print(current_local_dir)

    def do_pwd(self, arg):
        """Print current server directory."""
        print(self.access_path)

    def do_rename(self, arg):
        """Rename a file on the server."""
        args = arg.split()
        self.rename_handler(args)

    def do_rmdir(self, arg):
        args = arg.split()
        self.remove_dir_handler(args)

    def do_list(self, arg):
        """List files in the current server directory."""
        args = arg.split()
        self.list_handler(args)

    def do_ls(self, arg):
        """List files in the current server directory."""
        args = arg.split()
        self.list_handler(args)

    def do_llist(self, arg):
        """List local files."""
        args = arg.split()
        self.local_list_handler(args)

    def do_lls(self, arg):
        """List local files."""
        args = arg.split()
        self.local_list_handler(args)

    def do_lcd(self, arg):
        """Change the current local directory."""
        arg = arg.split()
        self.lcd_handler(arg)

    def do_quit(self, arg):
        """Exit the program."""
        self.exit_program()

    def do_exit(self, arg):
        """Exit the program."""
        self.exit_program()

    def do_mkdir(self, arg):
        """Make a directory on the server."""
        args = arg.split()
        self.make_dir_handler(args)

    def do_rm(self, arg):
        """Remove a file on the server."""
        args = arg.split()
        self.remove_file_handler(args)

    def do_resume(self, arg):
        """Resume a download."""
        args = arg.split()
        self.resume_download_handler(args)

    def upload_file_handler(self, arg):
        dir_path = process_path(arg[0], current_local_dir)
        if len(arg) > 1:
            if not validate_path(dir_path, file_check=True):
                print("Invalid path")

        file_data = get_file_info(dir_path)
        transmit_socket, port = create_transmit_socket()
        file_data["transmit_port"] = port
        file_name = os.path.basename(file_data["file_path"])
        StandardQuery(self.auth_token, command="upload", command_args=arg,
                      current_dir=self.access_path, data=file_data).serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            send_file.send_file(dir_path, transmit_socket, file_data["file_size"], file_name, True)
            response2 = rp.response_parser(self.user_socket.recv(4096))
            print(response2)
            if response2["accept"]:
                print("File uploaded successfully.")
                transmit_socket.close()
                return
            else:
                print("File upload failed.")
                self.handle_error(response2)
                transmit_socket.close()
                return
        else:
            self.handle_error(response)

    def download_file_handler(self, args):
        StandardQuery(self.auth_token, command="download", command_args=args,
                      current_dir=self.access_path).serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        dir_path = current_local_dir
        if len(args) > 1:
            dir_path = process_path(args[1], current_local_dir)
            if not validate_path(dir_path, dir_check=True):
                print("Invalid path")
                return
        if response["accept"]:
            transmit_port = int(response["data"]["transmit_port"])
            filename = os.path.basename(response["data"]["file_path"])
            filesize = int(response["data"]["file_size"])
            transmit_buffer_size = int(response["data"]["buffer_size"])
            checksum = response["data"]["checksum"]
            transmit_result = receive_file.retrieve_file(dir_path, transmit_port, filename, filesize,
                                                         transmit_buffer_size, checksum)
            if transmit_result:
                print("File downloaded successfully")
            else:
                print("File download failed.")
        else:
            self.handle_error(response)

    def list_handler(self, args):
        """List files in the current server directory."""
        terminal_width = shutil.get_terminal_size().columns
        query = StandardQuery(self.auth_token, "list", self.access_path, command_args=args,
                              data={"terminal_width": terminal_width})
        query.serialize_and_send(self.user_socket)
        print("Server dir list:\n")
        self.handle_response('', )

    def local_list_handler(self, args):
        dir_path = process_path(current_local_dir,current_local_dir)
        if args:
            dir_path = process_path(args[0],current_local_dir)


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

    def lcd_handler(self,arg):
        global current_local_dir
        try:
            if len(arg) == 0:
                print("Syntax Error.\nUsage: lcd <dir_path>")
                return
            dir_path = process_path(arg[0],current_local_dir)
            if not validate_path(dir_path, dir_check=True):
                raise NotADirectoryError
            current_local_dir = dir_path
            print("Local directory changed successfully.")
        except NotADirectoryError:
            print(f"Path: {dir_path} is not a directory.")
        except Exception as e:
            print(f"An error occurred: {e}")
        

    def change_dir_handler(self, args):
        """Change the current server directory."""
        query = StandardQuery(self.auth_token, "cd", self.access_path, command_args=args)
        query.serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            self.access_path = response["data"]["current_directory"]
            print("Changed directory successfully.")
        else:
            self.handle_error(response)

    def rename_handler(self, args):
        """Rename a file on the server."""
        query = StandardQuery(self.auth_token, "rename", self.access_path, command_args=args)
        query.serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            print("Renamed successfully.")
        else:
            self.handle_error(response)

    def handle_response(self, field: str):
        """Handle the server's response to a command."""
        raw_response = self.user_socket.recv(4096)
        if raw_response:
            response = rp.response_parser(raw_response)
            if response["accept"]:
                if field:
                    print(response["data"][field])
                else:
                    print(response["data"])
            else:
                self.handle_error(response)
        else:
            print("Failed to get response. Check your connection.")

    def make_dir_handler(self, args):
        """Make a directory on the server."""
        query = StandardQuery(self.auth_token, "mkdir", self.access_path, command_args=args)
        query.serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            print("Directory created successfully.")
        else:
            self.handle_error(response)

    def remove_dir_handler(self, args):
        """Remove a directory on the server."""
        if input("Are you sure you want to remove this directory? [y/N]: ") == "y":
            if len(args) > 0 and "-r" in args:
                data = {"method":"r"} # r Represents normal remove directory
                args = [i for i in args if i != "-r"]
            else:
                data = {"method":"n"} # n Represents normal remove directory
            query = StandardQuery(self.auth_token, "rmdir", self.access_path, command_args=args,data=data)
            query.serialize_and_send(self.user_socket)
            response = rp.response_parser(self.user_socket.recv(4096))
            if response["accept"]:
                print("Directory removed successfully.")
            else:
                self.handle_error(response)

    def remove_file_handler(self, args):
        """Remove a file on the server."""
        if input("Are you sure you want to remove this file? [y/N]: ") == "y":
            query = StandardQuery(self.auth_token, "rm", self.access_path, command_args=args)
            query.serialize_and_send(self.user_socket)
            response = rp.response_parser(self.user_socket.recv(4096))
            if response["accept"]:
                print("File removed successfully.")
            else:
                self.handle_error(response)

    def resume_download_handler(self, args):
        """Resume a download."""
        pass  # Implement as needed

    def handle_error(self, response):
        """Handle errors based on the server's response status code."""
        status_code = response["status_code"]
        error_messages = {
            FTPStatus.PATH_NOT_DIRECTORY: "Path is not a directory.",
            FTPStatus.FILE_UNAVAILABLE: "File not found in this directory.",
            FTPStatus.PERMISSION_DENIED: "Permission denied.",
            FTPStatus.SYNTAX_ERROR_IN_PARAMETERS: "Syntax error.",
            FTPStatus.FILE_EXISTS_ERROR: "File exists.",
            FTPStatus.LOCAL_ERROR_IN_PROCESSING: "Unknown error.",
            FTPStatus.NOT_LOGGED_IN: "You are not logged in.\nPlease log in with 'login' command.",
        }
        print(error_messages.get(status_code, "An unknown error occurred."))
        if response["data"]:
            print(response["data"])

    def help_full(self):
        """Display help information."""
        file_path = os.path.abspath("/home/ehsan/Workspace/FTP/help.txt")
        try:
            with open(file_path, "rt") as f:
                help_content = f.read()
                print(help_content)
        except FileNotFoundError:
            print("Help file not found.")

    def exit_program(self):
        """Close the user socket and exit the program."""
        self.user_socket.close()
        print("Connection closed. Exiting the program.")
        sys.exit(0)
