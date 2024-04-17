import requests
import json

TOKEN = '6380884350:AAFRxB35XYeYtzC6QHxeQ9Vq7xmJo9iEvkI'
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(URL)
updates = json.dumps(response.json(), indent = 4)

print(updates)
