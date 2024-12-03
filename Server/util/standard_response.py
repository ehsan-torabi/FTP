import json


class StandardResponse:
    def __init__(self, accept: bool, status_code: int, data: any = None):
        self.accept = accept
        self.status_code = status_code
        self.data = data

    def serialize(self):
        query_data = {"accept": self.accept, "status_code": self.status_code, "data": self.data}
        return json.dumps(query_data, ensure_ascii=False)

    def serialize_and_send(self,connection):
        serialized = self.serialize()
        connection.send(serialized.encode('utf-8'))