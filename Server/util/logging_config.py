import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

SERVER_START_PATH = os.getcwd()

def setup_logging(log_dir='logs'):
    """
    Set up comprehensive logging configuration for the FTP server.

    Args:
        log_dir (str): Directory to store log files. Defaults to 'logs'.
    """

    log_path = os.path.join(SERVER_START_PATH, log_dir)
    os.makedirs(log_path, exist_ok=True)


    log_filename = os.path.join(log_path, f'ftp_server_{datetime.now().strftime("%Y%m%d")}.log')


    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )


    logger = logging.getLogger('FTPServer')
    logger.setLevel(logging.INFO)


    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)


    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]')
    file_handler.setFormatter(file_formatter)


    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger



server_logger = setup_logging()