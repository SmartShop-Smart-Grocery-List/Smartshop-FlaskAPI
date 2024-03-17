# import requests

# BASE = "http://localhost:5000/"

# response = requests.post(BASE + "user", {'username': "Bob"})
# print(response.json())

# # response = requests.get(BASE + "user", {'username': "Bob"})
# # print(response.json())

# # response = requests.get(BASE + "recommend", {'username': "Bob"})
# # print(response.json())

# from main import read_recipe_ratings

# print(read_recipe_ratings().head())

from datetime import datetime
from suntime import Sun, SunTimeException
month = datetime.today().strftime("%m")

print(month)

sun = Sun(33.6695, -117.8231)
print(sun.get_sunrise_time(), )