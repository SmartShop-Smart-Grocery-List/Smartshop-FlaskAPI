from flask_restful import Resource, reqparse
from flask import abort
from app.db.models import RecipeRating as DBRecipeRatings, db, User as DBUsers
from model.preprocessing import preprocess
from model.recommendation.recommend import get_recipes_with_configuration

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

put_parser = reqparse.RequestParser()
put_parser.add_argument("username", type=str, help="Enter Username", location='args', required=True)
put_parser.add_argument("recipe_id", type=int, help="Enter the id of the recipe", location='args', required=True)
put_parser.add_argument("rating", type=int, help="Enter the rating, integer from 0 to 5 inclusive", location='args',
                        required=True)


class Recipe(Resource):
    def get(self):
        args = get_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if preprocess.data.is_user_in_filter(user.user_id):
            resp = get_recipes_with_configuration(preprocess.data.recipes, user.user_id, (
                    preprocess.data.user_interactions['user_id'] == user.user_id).sum(),
                                                  colab_filter=preprocess.data.recipe_colab_filter,
                                                  calories=args['calories'], daily=user.goal_daily_calories,
                                                  fat=args['fat'], sat_fat=args['sat fat'],
                                                  sugar=args['sugar'], sodium=args['sodium'], protein=args['protein'],
                                                  carbs=args['carbs'], tags=args['tags'])
        else:
            resp = get_recipes_with_configuration(preprocess.data.recipes, user.user_id, 0, colab_filter=None,
                                                  calories=args['calories'], daily=user.goal_daily_calories,
                                                  fat=args['fat'], sat_fat=args['sat fat'],
                                                  sugar=args['sugar'], sodium=args['sodium'], protein=args['protein'],
                                                  carbs=args['carbs'], tags=args['tags'])
        return resp[:5].to_dict()

    def put(self):
        args = put_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if not args['rating'] in [0, 1, 2, 3, 4, 5]:
            abort(400, {'error': 'Rating not integer in range [0, 5]'})

        if not args['recipe_id'] in preprocess.data.recipes['id'].values:
            abort(404, {'error': 'Invalid recipe_id'})

        new_rating = DBRecipeRatings(user_id=user.user_id, recipe_id=args['recipe_id'], rating=args['rating'])
        db.session.add(new_rating)
        db.session.commit()

        return {"data": {"username": args['username']}}, 201
