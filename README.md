

# FTP Server and Client

## Overview
This project implements a simple FTP (File Transfer Protocol) server and client, allowing users to upload, download, and manage files on a remote server. The server handles multiple user connections and provides various commands for file management.

## Features
- User authentication with login functionality.
- File upload and download capabilities.
- Directory management (create, remove, change directories).
- File management (rename, remove files).
- List and display directory contents.
- Support for multiple concurrent users.

## Technologies Used
- Python
- Socket Programming
- Object-Oriented Programming
- File System Operations

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/EhsanT0rabi/FTP
   cd FTP
   ```

2. Install any required dependencies (if applicable):
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure that Python is installed on your system (Python 3.x is recommended).

## Usage
### Starting the Server
1. Navigate to the server directory.
2. Run the server script:
   ```bash
   python Server/server.py
   ```
3. The server will start and listen for incoming connections.

### Connecting with the Client
1. Navigate to the client directory.
2. Run the client script:
   ```bash
   python Client/client.py
   ```
3. Enter the server port when prompted to connect to the server.

### Available Commands
- `login <username@password>`: Authenticate the user.
- `upload <filename>`: Upload a file to the server.
- `download <filename>`: Download a file from the server.
- `resume` : Resume last failed downloaded file (Stored in client-side).
- `mkdir <directory_name>`: Create a new directory on the server.
- `rmdir <directory_name>`: Remove a directory from the server.
- `cd <directory_name>`: Change the current working directory.
- `list <directory_name>` or `ls <directory_name>` : List files in the current directory or passed path.
- `rename <old_name> <new_name>`: Rename a file or directory.
- `rm <filename>`: Remove a file from the server.
- `help`: Display help information.
- `quit` or `exit`: Close the connection and exit the client.

## Contributing
Contributions are welcome! If you have suggestions or improvements, please create a pull request or open an issue.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
- [Python Documentation](https://docs.python.org/3/)
- [Socket Programming in Python](https://realpython.com/python-sockets/)
