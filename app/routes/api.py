from flask_restful import Api

from app.routes.users import User
from app.routes.recipes import Recipe
from app.routes.exercises import Exercise
from app.routes.diets import DietRecommendation
# from app.routes.recommendation import  Recommendation
# from app.routes.fitbit_data import FitbitData
from app.routes.lifestyle_score import LifestyleScore

api = Api()

api.add_resource(Recipe, "/recommend/recipes")
api.add_resource(Exercise, "/recommend/exercises")
api.add_resource(DietRecommendation, "/recommend/diets")
api.add_resource(User, "/users")
# api.add_resource(Recommendation, "/recommend")
# api.add_resource(FitbitData, "/fitbit-data")
api.add_resource(LifestyleScore, "/lifestyle")