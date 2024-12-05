import bz2
import json


def response_parser(response):
    decompressed = bz2.decompress(response)
    return json.loads(decompressed)


def request_parser(response):
    return json.loads(response.decode('utf-8'))
