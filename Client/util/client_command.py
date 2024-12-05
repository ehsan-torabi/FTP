import os
import pathlib
import shutil
import socket
import cmd
import sys

from utils import receive_file
from utils import request_parser as rp
from utils.ftp_status_code import FTPStatusCode as FTPStatus
from utils.standard_query import StandardQuery

# Set the current server and local directories
current_server_dir = "."
current_local_dir = os.path.dirname(os.path.abspath(__file__))

class FTPClient(cmd.Cmd):
    intro = 'Welcome to the FTP client. Type help or ? to list commands.'
    prompt = '(ftp) '

    def __init__(self, user_socket):
        super().__init__()
        self.user_socket = user_socket

    def do_login(self, arg):
        """Handle user login."""
        pass

    def do_upload(self, arg):
        """Upload a file to the server."""
        self.upload_file_handler()

    def do_download(self, arg):
        """Download a file from the server."""
        args = arg.split()
        self.download_file_handler(args)

    def do_cd(self, arg):
        """Change the current server directory."""
        args = arg.split()
        self.change_dir_handler(args)

    def do_ldir(self, arg):
        """Print current local directory."""
        print(current_local_dir)

    def do_dir(self, arg):
        """Print current server directory."""
        print(current_server_dir)

    def do_rename(self, arg):
        """Rename a file on the server."""
        args = arg.split()
        self.rename_handler(args)

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

    def do_help(self, arg):
        """Display help information."""
        self.help_handler()

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

    def do_rmdir(self, arg):
        """Remove a directory on the server."""
        args = arg.split()
        self.remove_dir_handler(args)

    def do_rm(self, arg):
        """Remove a file on the server."""
        args = arg.split()
        self.remove_file_handler(args)

    def do_resume(self, arg):
        """Resume a download."""
        args = arg.split()
        self.resume_download_handler(args)

    def upload_file_handler(self):
        pass

    def download_file_handler(self, args):
        StandardQuery(auth_token="1234", command="download", command_args=args,
                      current_dir=current_server_dir).serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            transmit_port = int(response["data"]["transmit_port"])
            filename = os.path.basename(response["data"]["file_path"])
            filesize = int(response["data"]["file_size"])
            transmit_buffer_size = int(response["data"]["buffer_size"])
            checksum = response["data"]["checksum"]
            transmit_result = receive_file.retrieve_file(self.user_socket, current_local_dir, transmit_port, filename, filesize,
                                                         transmit_buffer_size, checksum, True)
            if transmit_result:
                print("File downloaded successfully")
        else:
            self.handle_error(response)

    def list_handler(self, args):
        """List files in the current server directory."""
        terminal_width = shutil.get_terminal_size().columns
        query = StandardQuery("1234", "list", current_server_dir, command_args=args,
                              data={"terminal_width": terminal_width})
        query.serialize_and_send(self.user_socket)
        print("Server dir list:\n")
        self.handle_response('',)

    def local_list_handler(self, args):
        dir_path = os.path.abspath(current_local_dir)
        if args:
            dir_path = os.path.abspath(os.path.join(current_local_dir, args[0]))
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

    def change_dir_handler(self, args):
        """Change the current server directory."""
        global current_server_dir
        query = StandardQuery("1234", "cd", current_server_dir, command_args=args)
        query.serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            current_server_dir = response["data"]["current_directory"]
            print("Changed directory successfully.")
        else:
            self.handle_error(response)

    def rename_handler(self, args):
        """Rename a file on the server."""
        query = StandardQuery("1234", "rename", current_server_dir, command_args=args)
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
        query = StandardQuery("1234", "mkdir", current_server_dir, command_args=args)
        query.serialize_and_send(self.user_socket)
        response = rp.response_parser(self.user_socket.recv(4096))
        if response["accept"]:
            print("Directory created successfully.")
        else:
            self.handle_error(response)

    def remove_dir_handler(self, args):
        """Remove a directory on the server."""
        pass  # Implement as needed

    def remove_file_handler(self, args):
        """Remove a file on the server."""
        pass  # Implement as needed

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
        }
        print(error_messages.get(status_code, "An unknown error occurred."))
        if "data" in response:
            print(response["data"])

    def help_handler(self):
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



