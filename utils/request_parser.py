import bz2
import json


def server_response_parser(response):
    decompressed = bz2.decompress(response)
    return json.loads(decompressed)


def client_response_parser(response):
    return json.loads(response.decode('utf-8'))
