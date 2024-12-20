import socket as s
import sys

from Client.client_command import FTPClient


def start_cycle(usr_socket, ip):
    """Continuously prompt the user for input and process commands."""
    while True:
        try:
            FTPClient(usr_socket, ip).cmdloop(intro="[+] You are connected.\nUse 'help' to see commands.")
        except TimeoutError:
            print("Timeout Error: Check your connection.")
        except Exception as e:
            print(f"An error occurred: {e}")


def connect_to_server(ip, port):
    """Establish a connection to the FTP server."""
    try:
        with s.socket(s.AF_INET, s.SOCK_STREAM) as soc:
            soc.connect((str(ip), int(port)))
            start_cycle(soc, ip)
    except ValueError:
        print("Invalid port number. Please enter a valid integer.")
    except ConnectionRefusedError:
        print("Connection refused. Please check the server address and port.")
    except Exception as e:
        print(f"An error occurred while connecting: {e}")


def main(ip="127.0.0.1", port=8021):
    connect_to_server(ip, port)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], int(sys.argv[2]))
    else:
        main()
