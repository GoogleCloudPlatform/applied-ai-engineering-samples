import os
import re

with open('message.proto', 'r') as f:
    proto_str = f.read()


proto_str = proto_str.replace('\n', '\\n').replace('"', r'\"')
print(proto_str)


