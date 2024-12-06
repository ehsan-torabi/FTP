import hashlib
import os
import socket
from typing import Optional, Tuple

from tqdm import tqdm

from utils.AES_handler import AES_decryptor

DELIMITER = '<SEPARATOR>'


def retrieve_file(
        file_path: str,
        transmit_port: int,
        file_name: str,
        file_size: int,
        buffer_size: int,
        checksum: str,
        progress_bar: bool = True,
        timeout: float = 30.0
) -> Tuple[bool, Optional[str]]:
    """
    Retrieve and decrypt a file from a socket connection.

    Args:
        file_path (str): Directory to save the file
        transmit_port (int): Port to connect to
        file_name (str): Name of the file to save
        file_size (int): Expected file size
        buffer_size (int): Size of data chunks to receive
        checksum (str): Expected MD5 checksum
        progress_bar (bool): Whether to show progress
        timeout (float): Socket timeout in seconds

    Returns:
        Tuple[bool, Optional[str]]:
        - First value: Success of file retrieval and verification
        - Second value: Error message if failed, None if successful
    """
    transmit_socket = None
    progress = None
    full_file_path = os.path.join(file_path, file_name)

    try:
        # Create socket with timeout
        transmit_socket = socket.create_connection(("localhost", transmit_port), timeout=timeout)


        # Create progress bar if requested
        if progress_bar:
            progress = tqdm(
                range(file_size),
                f"Receiving {file_name}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            )




        with open(full_file_path, "wb") as f:
            total_received = 0
            while total_received < file_size:
                # Receive data chunk
                bytes_read = transmit_socket.recv(buffer_size)

                if not bytes_read:
                    return False, "Connection closed unexpectedly"

                if bytes_read == b"EOF":
                    break

                # Handle last chunk
                if bytes_read[-3:] == b"EOF":
                    f.write(bytes_read[:-3])
                    total_received += len(bytes_read)
                    break

                # Decrypt and write data
                f.write(bytes_read)
                total_received += len(bytes_read)

                # Update progress bar
                if progress_bar and progress:
                    progress.update(len(bytes_read))

        # Verify file checksum
        with open(full_file_path, "rb") as file:
            new_checksum = hashlib.file_digest(file, "md5").hexdigest()
            if checksum != new_checksum:
                return False, "Checksum verification failed"

        return True, None

    except socket.timeout:
        return False, "Socket connection timed out"
    except PermissionError:
        return False, "Permission denied when writing file"
    except OSError as e:
        return False, f"OS error occurred: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"
    finally:
        # Ensure socket is closed
        if transmit_socket:
            transmit_socket.close()

        # Close progress bar
        if progress_bar and progress:
            progress.close()