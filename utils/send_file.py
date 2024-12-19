import hashlib
import logging
import pathlib
import socket
from random import randint
from typing import Dict, Tuple

from tqdm import tqdm

BUFFER_SIZE = 4096
MAX_PORT_ATTEMPTS = 100  # Limit port binding attempts


def create_transmit_socket(server_addr:str,max_attempts: int = MAX_PORT_ATTEMPTS) -> Tuple[socket.socket, int]:
    """
    Create a socket and bind to a random available port.

    Args:
        max_attempts (int): Maximum number of attempts to find an available port

    Returns:
        Tuple of (socket, port number)

    Raises:
        OSError: If unable to bind to a port after max attempts
    """
    transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transmit_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for attempt in range(max_attempts):
        try:
            port = randint(1024, 65535)
            transmit_socket.bind((server_addr, port))
            transmit_socket.listen(1)
            return transmit_socket, port
        except OSError:
            if attempt == max_attempts - 1:
                raise OSError(f"Could not bind to a port after {max_attempts} attempts")

    raise OSError("Unexpected error in port binding")


def get_file_info(file_path: str) -> Dict[str, any]:
    """
    Retrieve comprehensive file information.

    Args:
        file_path (str): Path to the file

    Returns:
        Dictionary with file metadata

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If path is not a file
    """
    try:
        file_path_object = pathlib.Path(file_path).resolve()

        if not file_path_object.is_file():
            raise ValueError(f"Path {file_path} is not a file")

        filesize = file_path_object.stat().st_size

        with open(file_path_object, "rb") as file:
            checksum = hashlib.file_digest(file, "md5").hexdigest()

        return {
            "file_path": str(file_path_object),
            "file_size": filesize,
            "buffer_size": BUFFER_SIZE,
            "checksum": checksum
        }
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"File access error: {e}")
        raise


def send_file(
        file_path: str,
        transmit_socket: socket.socket,
        filesize: int,
        filename: str,
        progress_bar: bool = True,
        timeout: float = 30.0
) -> bool:
    """
    Send an encrypted file over a socket connection.

    Args:
        file_path (str): Path to the file to send
        transmit_socket (socket.socket): Established socket
        filesize (int): Size of the file
        filename (str): Name of the file
        progress_bar (bool): Whether to show progress
        timeout (float): Socket operation timeout

    Returns:
        bool: Whether file was successfully sent
    """
    try:
        # Set socket timeout
        transmit_socket.settimeout(timeout)

        # Accept connection
        transmit_connection, addr = transmit_socket.accept()

        # Optional progress bar
        progress = None
        if progress_bar:
            progress = tqdm(
                range(filesize),
                f"Sending {filename}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            )

        try:
            with transmit_connection, open(file_path, "rb") as f:
                total_sent = 0
                while total_sent < filesize:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        transmit_connection.send(b"EOF")
                        break
                    transmit_connection.send(bytes_read)

                    total_sent += len(bytes_read)

                    if progress_bar and progress:
                        progress.update(len(bytes_read))

        finally:
            # Ensure progress bar is closed
            if progress_bar and progress:
                progress.close()

        return True

    except (socket.timeout, ConnectionError) as e:
        logging.error(f"Network error during file send: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during file send: {e}")
        return False
    finally:
        # Ensure socket is closed
        transmit_socket.close()
