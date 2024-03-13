import requests

BASE = "http://localhost:5000/"

response = requests.post(BASE + "user", {'username': "Bob"})
print(response.json())

# response = requests.get(BASE + "user", {'username': "Bob"})
# print(response.json())

# response = requests.get(BASE + "recommend", {'username': "Bob"})
# print(response.json())