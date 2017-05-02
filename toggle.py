from requests import get

url = 'http://192.168.1.128/toggle'
headers = {'x-ha-access': 'raspberry',
'content-type': 'application/json'}

response = get(url, headers=headers)