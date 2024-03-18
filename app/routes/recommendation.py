from flask_restful import Resource, reqparse
from flask import abort
from app.db.models import RecipeRating as DBRecipeRatings, db, User as DBUsers
from model.preprocessing import preprocess
from model.recommendation.recommend import Recommender
from model.personalization.personalization import Personalizer
from model.contextualization.context import Context

get_parser = reqparse.RequestParser()

get_parser.add_argument("username", type=str, help="Enter Username", location='args', required=True)
get_parser.add_argument("calories", type=int, help="Number of calories of the food", location='args')
get_parser.add_argument("fat", type=str, help="Total Fat (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("sat_fat", type=str, help="Saturated Fat (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("sugar", type=str, help="Sugar (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("sodium", type=str, help="Sodium (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("protein", type=str, help="Protein (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("carbs", type=str, help="Carbohydrates (PDV): 'high' or 'mid' or 'low'", location='args')
get_parser.add_argument("tags", type=list, help="Tags that must be on the food", location='args')


class Recipe(Resource):
    def get(self):
        args = get_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        current_context = args
        personalizator = db.session.query(DBUsers).where(DBUsers.username == args['username']).first()

        context = Context(current_context)
        personalized = Personalizer(personalizator)
        recommender = Recommender(context, personalized)

        if not user:
            abort(404, {'error': 'User not found'})

        recommendation = recommender.get_recommendation()
        return recommendation, 200
