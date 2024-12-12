import socket as s
import sys
from Client.util.client_command import FTPClient

def start_cycle(usr_socket):
    """Continuously prompt the user for input and process commands."""
    while True:
        try:
            FTPClient(usr_socket).cmdloop(intro="[+] You are connected.\nUse 'help' to see commands.")
        except TimeoutError:
            print("Timeout Error: Check your connection.")
        except Exception as e:
            print(f"An error occurred: {e}")


def connect_to_server(port):
    """Establish a connection to the FTP server."""
    try:
        with s.socket(s.AF_INET, s.SOCK_STREAM) as soc:
            soc.connect(('127.0.0.1', int(port)))
            start_cycle(soc)
    except ValueError:
        print("Invalid port number. Please enter a valid integer.")
    except ConnectionRefusedError:
        print("Connection refused. Please check the server address and port.")
    except Exception as e:
        print(f"An error occurred while connecting: {e}")


def main(port=8021):
    connect_to_server(port)


if __name__ == "__main__":
    if len(sys.argv) == 2:
         main(int(sys.argv[1]))
    else:
        main()
