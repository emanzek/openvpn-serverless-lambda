import requests
import json

url = "http://localhost:3000/common"

with open('./event.json','r') as file:
    payload = json.load(file)
    response = requests.request("POST", url, data=json.dumps(payload))

print(response.text)
