from flask_restful import Resource, reqparse
from flask import abort
from app.db.models import RecipeRating as DBRecipeRatings, db, User as DBUsers
from model.contextualization.context import Context
from model.personalization.personalization import Personalizer
from model.preprocessing import preprocess
from model.recommendation.recommend import Recommender

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
    """
    Resource class for handling recipe-related requests.

    Methods:
        get(self): Retrieves recipe recommendations based on user preferences.
        put(self): Records user ratings for recipes.
    """

    def get(self):
        """
        Retrieves recipe recommendations based on user preferences.

        Returns:
            dict: Dictionary containing recipe recommendations.
        """
        args = get_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        context = Context(args.__dict__)

        personalizer_config = {
            "user_id": user.user_id,
            "user_ratings_count": 0
        }

        personalizer = Personalizer(user=personalizer_config)

        rec = Recommender(context=context, personalizer=personalizer)

        if preprocess.data.is_user_in_filter(user.user_id):
            personalizer['user_ratings_count'] = preprocess.data.user_interactions['user_id'] == user.user_id.sum()
            resp = rec.get_recipes_with_configuration(preprocess.data.recipes,
                                                      colab_filter=preprocess.data.recipe_colab_filter)
        else:
            resp = rec.get_recipes_with_configuration(preprocess.data.recipes, colab_filter=None)
        return resp[:5].to_dict()

    def put(self):
        """
        Records user ratings for recipes.

        Returns:
            dict: Acknowledgment message.
        """
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
