import json
from datetime import datetime


class ChatMessage:
    def __init__(self, src=None, dst=None, txt=None):
        self.src = src
        self.dst = dst
        self.txt = txt
        self.time = str(datetime.now())
        self.data = {
            'src': self.src,
            'dst': self.dst,
            'txt': self.txt,
            'time': self.time,
        }

    def as_json(self):
        return json.dumps(self.data, indent=1) + '\n\n\n'

    def from_json(self, json_text):
        json_message_text = json_text.split('\n\n\n')[0]
        remainder = '\n\n\n'.join(json_text.split('\n\n\n')[1:])
        self.data = json.loads(json_message_text)
        self.src = self.data['src']
        self.dst = self.data['dst']
        self.txt = self.data['txt']
        self.time = self.data['time']
        return self, remainder
