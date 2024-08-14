import requests
import json
import datetime

url = "http://localhost:3000/common"
filepath = './event.json'

def main():
    payload = read_json(filepath)    
    response = requests.request("POST", url, data=json.dumps(payload))
    print(response.text)

def read_json(data):
    with open(data,'r') as file:
        data = json.load(file)
        
        # Update timestamp to current time
        time_now = int(datetime.datetime.now().timestamp())
        data['message']['date'] = time_now
        
    return data

if __name__ == "__main__":
    main()