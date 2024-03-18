import requests

BASE = "http://localhost:5000/"

response = requests.put(BASE + "user", {'username': "Bob",
                                         'age': "20",
                                         'height': "130",
                                         'weight': "170",
                                         'gender': 'M',
                                         'current_level_of_activity': 'moderately active',
                                         'goal_level_of_activity': 'moderately active',
                                         'goal_daily_calories': 2200,
                                         'weight_goal': 'gain'})
print(response.json())

response = requests.get(BASE + "recommend/recipe", {'username': "Bob",
                                             'calories': 400,
                                             'tags': ["vegan"]})
print(response.json())

response = requests.get(BASE + "lifestyle", {'username': "Bob"})