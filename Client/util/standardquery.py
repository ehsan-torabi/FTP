import json

from utils.command_codes import commands_code_dict


class StandardQuery:
    def __init__(self, auth_token: str, command: str | int, current_dir: str = None, command_args: list[str] = None,
                 data: any = None):
        self.auth_token = auth_token
        self.command = command
        self.command_args = command_args
        self.data = data
        self.current_dir = current_dir

    def serialize(self):
        query_dict = {"auth_token": self.auth_token}
        try:
            if not self.command.isnumeric():
                self.command = commands_code_dict[self.command]
            query_dict["command"] = self.command
        except KeyError:
            print("Invalid command")
        query_dict["command_args"] = {}
        if self.command_args:
            for num, arg in enumerate(self.command_args):
                query_dict["command_args"][num] = arg
        query_dict["current_dir"] = self.current_dir
        query_dict["data"] = self.data
        return json.dumps(query_dict, ensure_ascii=False)

    def serialize_and_send(self, connection):
        serialized = self.serialize()
        connection.sendall(serialized.encode("utf-8"))
