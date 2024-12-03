import json


def server_response_parser(response):
    return json.loads(response)

def client_response_parser(response):
    return json.loads(response)