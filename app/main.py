from flask import Flask, abort
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.recommender.recommendation.recommend import getRecipesWithConfiguration
from app.recommender import data_management

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///user_database.db',
    'recipe_ratings': 'sqlite:///recipe_ratings_database.db'
}
db = SQLAlchemy(app)




class DietRecommendation(Resource):
    def get(self):
        args = diet_recommendation_get_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if not user.weight_goal:
            abort(400, {'error': 'User does not have a weight goal'})
        
        if not (user.age and user.height and user.weight and user.gender and user.current_level_of_activity):
            abort(400, {'error': 'One of: age, height, weight, gender, current_level_of_of_activity missing'})
                
        w = user.weight * 0.45359237
        h = user.height * 2.54
        a = user.age
        bmr = 0
        abmr = 0
        loa_labels = [('sedentary', 1.2), ('lightly active', 1.375), ('moderately active', 1.55), ('active', 1.725), ('very active', 1.9)]
        loa = 0

        recommendation_options = {}

        match user.gender:
            case 'M':
                bmr = 10 * w + 6.25 * h - 5 * a + 5
            case 'F':
                bmr = 10 * w + 6.25 * h - 5 * a - 161

        match user.current_level_of_activity:
            case 'sedentary':
                loa = 0
            case 'lightly active':
                loa = 1
            case 'moderately active':
                loa = 2
            case 'active':
                loa = 3
            case 'very active':
                loa = 4
        
        abmr = bmr * loa_labels[loa][1]
        
        match user.weight_goal:
            case 'lose':
                if loa < 4:
                    option = {}
                    option_abmr = bmr * loa_labels[loa+1][1]
                    lb_loss = round((option_abmr - abmr) / 500, 1)
                    
                    option['comment'] = f"Increase level of activity to {loa_labels[loa+1][0]} to lose {lb_loss} lbs per week."
                    option['goal_daily_calories'] = user.current_daily_calories
                    option['goal_level_of_activity'] = loa_labels[loa+1][0]
                    recommendation_options['option_1'] = option
                
                option = {}
                option_abmr = (bmr * loa_labels[loa][1]) - 350 if (bmr * loa_labels[loa][1]) - 350 >= 1500 else 1500
                lb_loss = round((option_abmr - abmr) / 500, 1)

                option['comment'] = f"Reduce calories to {option_abmr} to lose {lb_loss} lbs per week."
                option['goal_daily_calories'] = option_abmr
                option['goal_level_of_activity'] = user.current_level_of_activity
                recommendation_options['option_2'] = option

            case 'gain':
                if loa > 2:
                    option = {}
                    option_abmr = bmr * loa_labels[loa-1][1]
                    lb_gain = round((abmr - option_abmr) / 500, 1)
                    
                    option['comment'] = f"Decrease level of activity to {loa_labels[loa-1][0]} to gain {lb_gain} lbs per week."
                    option['goal_daily_calories'] = user.current_daily_calories
                    option['goal_level_of_activity'] = loa_labels[loa-1][0]
                    recommendation_options['option_1'] = option
                
                option = {}
                option_abmr = (bmr * loa_labels[loa][1]) + 350 if (bmr * loa_labels[loa][1]) + 350 >= 1500 else 1500
                lb_gain = round((abmr - option_abmr) / 500, 1)

                option['comment'] = f"Increase calories to {option_abmr} to hain {lb_gain} lbs per week."
                option['goal_daily_calories'] = option_abmr
                option['goal_level_of_activity'] = user.current_level_of_activity
                recommendation_options['option_2'] = option
            case 'maintain':
                option = {}
                option['comment'] = f"Eat {user.current_daily_calories} calories, and maintain {loa_labels[loa][0]} lifestyle to maintain weight."
                option['goal_daily_calories'] = user.current_daily_calories
                option['goal_level_of_activity'] = user.current_level_of_activity
                recommendation_options['option_1'] = option

exercise_get_args = reqparse.RequestParser()
exercise_get_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
exercise_get_args.add_argument("type", type=int, help="Enter the type of exercise", location='args')
exercise_get_args.add_argument("body_part", type=str, help="Enter the main body part the exercise is for", location='args')
exercise_get_args.add_argument("equipment", type=str, help="Enter the equipment used in the exercise", location='args')
exercise_get_args.add_argument("level", type=str, help="Enter the difficulty level", location='args')

recipe_put_args = reqparse.RequestParser()
recipe_put_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
recipe_put_args.add_argument("exercise_id", type=int, help="Enter the id of the exercise", location='args', required=True)
recipe_put_args.add_argument("rating", type=int, help="Enter the rating, integer from 0 to 5 inclusive", location='args', required=True)

class Exercise(Resource):
    def get(self):
        args = recipe_get_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})
        
        

        resp = getRecipesWithConfiguration(data_management.data.recipes, data_management.data.recipe_colab_filter,
                                           calories=args['calories'], daily=user.goal_daily_calories,
                                           fat=args['fat'], sat_fat=args['sat fat'],
                                           sugar=args['sugar'], sodium=args['sodium'], protein=args['protein'],
                                           carbs=args['carbs'], tags=args['tags'])
        
        return resp[:5].to_dict()
    
    def put(self):
        args = recipe_put_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if not args['rating'] in [0, 1, 2, 3, 4, 5]:
            abort(400, {'error': 'Rating not integer in range [0, 5]'})

        # TODO
        if not args['exercise_id'] in data_management.data.exercises['id'].values:
            abort(404, {'error': 'Invalid recipe_id'})
        
        new_rating = DBExerciseRatings(user_id=user.user_id, exercise_id=args['exercise_id'], rating=args['rating'])
        db.session.add(new_rating)
        db.session.commit()
        
        return {"data": {"username": args['username']}}, 201
    
api.add_resource(Recipe, "/recommend/recipe")
api.add_resource(Exercise, "/recommend/exercise")
api.add_resource(DietRecommendation, "/recommend/diet")
api.add_resource(User, "/user")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        data_management.data = data_management.DataManager()
        data_management.data.setup_recipe_colab_filter()
    app.run(port=5000, debug=True)