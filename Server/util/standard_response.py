import json


class StandardResponse:
    def __init__(self,user_accept:bool,command_accept:bool,status_code:int,data:any=None):
        self.user_accept = user_accept
        self.command_accept = command_accept
        self.status_code = status_code
        self.data = data

    def serialize(self):
        query_data = {"user_accept":self.user_accept,"command_accept":self.command_accept,"status_code":self.status_code,"data":self.data}
        return json.dumps(query_data,ensure_ascii=False)


