from collections import namedtuple
from json import JSONEncoder
import json

class Message():

    body = ""
    sender = "unknown"
    
    def __init__(self, body, sender):
        self.body = body
        self.sender = sender

def toJSON(message: Message) -> str:
    print(message)
    return json.dumps(message, cls=MessageEncoder)


class MessageEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def customMessageDecoder(messageDict):
    return namedtuple('message', messageDict.keys())(*messageDict.values())

def fromJSON(messageJson) -> Message:
    return json.loads(messageJson, object_hook=customMessageDecoder)
