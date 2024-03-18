from flask_restful import Resource, reqparse
from flask import abort
from app.db.models import RecipeRating as DBRecipeRatings, db, User as DBUsers, FitBit
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
get_parser.add_argument("type", type=int, help="Enter the type of exercise", location='args')
get_parser.add_argument("body_part", type=str, help="Enter the main body part the exercise is for",
                        location='args')
get_parser.add_argument("equipment", type=str, help="Enter the equipment used in the exercise", location='args')
get_parser.add_argument("level", type=str, help="Enter the difficulty level", location='args')



class Recommendation(Resource):
    """
    Resource class for providing personalized recommendations.

    Methods:
        get(self): Retrieves personalized recommendations for a user.
    """

    def get(self):
        """
        Retrieves personalized recommendations for a user.

        Returns:
            dict: Dictionary containing personalized recommendations.
        """
        args = get_parser.parse_args()
        user = db.session.query(DBUsers).where(DBUsers.username == args['user']).first()

        current_context = args
        personalizator = user
        fit_data = db.session.query(FitBit).where(FitBit.user_id == user.user_id).all()
        context = Context(current_context)
        personalized = Personalizer(personalizator, fit_data)
        recommender = Recommender()

        if not user:
            abort(404, {'error': 'User not found'})

        recommendation = recommender.get_recommendation(context, personalized)
        return recommendation, 200
