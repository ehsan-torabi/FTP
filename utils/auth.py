import hashlib

import bcrypt

from utils.request_parser import response_parser
from utils.standard_query import StandardQuery


def authorize(username, password,control_socket):
    StandardQuery(auth_token="",command="login",current_dir="",command_args=[f"{username}@{password}"],data="").serialize_and_send(control_socket)
    resp = control_socket.recv(1024)
    parsed_response = response_parser(resp)
    return parsed_response["data"]

def generate_user_auth_hash(username,addr):
    sha256 = hashlib.sha256()
    sha256.update(f"{username}@{addr}")
    return sha256.hexdigest()

def password_hash(password):
    hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hash

def check_password(hash_password,password):
    return bcrypt.checkpw(password.encode("utf-8"), hash_password)
