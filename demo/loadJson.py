import json

data = {}
with open("2019050706.json", "r") as read_json :
    data = json.loads(read_json.read())
print type(data[0])