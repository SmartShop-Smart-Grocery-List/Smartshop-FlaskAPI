from flask import Flask, abort
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from recommend import getRecipesWithConfiguration

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///user_database.db',
    'ratings': 'sqlite:///ratings_database.db'
}
db = SQLAlchemy(app)

class DBUsers(db.Model):
    __bind_key__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), nullable=False)
    current_daily_calories = db.Column(db.Integer)
    goal_daily_calories = db.Column(db.Integer)
    name = db.Column(db.String(256))
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    current_level_of_activity = db.Column(db.String(20))
    goal_level_of_activity = db.Column(db.String(20))
    weight_goal = db.Column(db.String(10))

    def __repr__(self):
        return f"""User(User ID = {self.user_id}, Username = {self.username}, Current Daily Calories = {self.current_daily_calories}, 
                Goal Daily Calories = {self.goal_daily_calories}, Name = {self.name}, Age = {self.age}, Height = {self.height}, 
                Weight = {self.weight}, Gender = {self.gender}, Current Level of Activity = {self.current_level_of_activity}, 
                Goal Level of Activity = {self.goal_level_of_activity}, Weight Goal = {self.weight_goal})"""

class DBRatings(db.Model):
    __bind_key__ = 'ratings'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Rating(User ID = {self.user_id}, RecipeID = {self.recipe_id}, Rating = {self.rating})"
    
user_post_args = reqparse.RequestParser()
user_post_args.add_argument('username', type=str, required=True, help='Username is required', location='form')
user_post_args.add_argument('current_daily_calories', type=int, help='Enter the current daily calories for this user', location='form')
user_post_args.add_argument('goal_daily_calories', type=int, help='Enter the goal daily calories for this user', location='form')
user_post_args.add_argument('name', type=str, help='Name of the user', location='form')
user_post_args.add_argument('age', type=int, help='Age of the user', location='form')
user_post_args.add_argument('height', type=int, help='Height of the user in inches', location='form')
user_post_args.add_argument('weight', type=int, help='Weight of the user in lbs', location='form')
user_post_args.add_argument('gender', type=str, help="Gender of the user ('M' or 'F')", location='form')
user_post_args.add_argument('current_level_of_activity', type=str,
    help="""Current level of activity: 'sedentary' (little or no exercise), 'lightly active' (exercise 1–3 days/week), 
'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 'very active' (hard exercise 6–7 days/week)]""",location='form')
user_post_args.add_argument('goal_level_of_activity', type=str,
    help="""Goal level of activity: 'sedentary' (little or no exercise), 
'lightly active' (exercise 1–3 days/week), 'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 
'very active' (hard exercise 6–7 days/week)]""", location='form')
user_post_args.add_argument('weight_goal', type=str, help="Weight goal: 'lose', 'gain', 'maintain'", location='form')

user_get_args = reqparse.RequestParser()
user_get_args.add_argument('username', type=str, required=True, help='Username is required', location='args')

user_put_args = reqparse.RequestParser()
user_put_args.add_argument('username', type=str, required=True, help='Username is required', location='args')
user_put_args.add_argument('current_daily_calories', type=int, help='Enter the current daily calories for this user', location='args')
user_put_args.add_argument('goal_daily_calories', type=int, help='Enter the goal daily calories for this user', location='form')
user_put_args.add_argument('name', type=str, help='Name of the user', location='args')
user_put_args.add_argument('age', type=int, help='Age of the user', location='args')
user_put_args.add_argument('height', type=int, help='Height of the user in inches', location='args')
user_put_args.add_argument('weight', type=int, help='Height of the user in inches', location='args')
user_put_args.add_argument('gender', type=str, help="Gender of the user ('M' or 'F')", location='args')
user_put_args.add_argument('current_level_of_activity', type=str,
    help="""Current level of activity: 'sedentary' (little or no exercise), 'lightly active' (exercise 1–3 days/week), 
'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 'very active' (hard exercise 6–7 days/week)]""",location='args')
user_put_args.add_argument('goal_level_of_activity', type=str,
    help="""Goal level of activity: 'sedentary' (little or no exercise), 
'lightly active' (exercise 1–3 days/week), 'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 
'very active' (hard exercise 6–7 days/week)]""", location='args')
user_put_args.add_argument('weight_goal', type=str, help="Weight goal: 'lose', 'gain', 'maintain'", location='args')

current_max_id = None

class User(Resource):
    def post(self):
        args = user_post_args.parse_args()

        if len(args['username']) > 128:
            abort(400, {'error': 'Username must be 128 characters or less'})

        username = args['username']
        user = DBUsers.query.filter_by(username=username).first()

        if user:
            abort(403, {'error': 'User already exists'})

        global current_max_id
        if current_max_id is None:
            current_max_id = db.session.query(db.func.max(DBUsers.user_id)).scalar() or 0

        new_user_data = {'user_id': current_max_id + 1, 'username': username}

        if args['current_daily_calories']:
            if args['current_daily_calories'] < 0:
                abort(400, {'error': 'Current daily calories must be a non-negative integer'})
            new_user_data['current_daily_calories'] = args['current_daily_calories']

        if args['goal_daily_calories']:
            if args['goal_daily_calories'] < 0:
                abort(400, {'error': 'Goal daily calories must be a non-negative integer'})
            new_user_data['goal_daily_calories'] = args['goal_daily_calories']

        if args['name']:
            if len(args['name']) > 256:
                abort(400, {'error': 'Name must be 256 characters or less'})
            new_user_data['name'] = args['name']
        
        if args['age']:
            if args['age'] < 0:
                abort(400, {'error': 'Age must be a non-negative integer'})
            elif args['age'] > 100:
                abort(400, {'error': 'Age must not be an integer greater than 100'})
            new_user_data['age'] = args['age']

        if args['height']:
            if args['height'] < 0:
                abort(400, {'error': 'Height must be a non-negative integer'})
            new_user_data['height'] = args['height']
        
        if args['weight']:
            if args['weight'] < 0:
                abort(400, {'error': 'Weight must be a non-negative integer'})
            new_user_data['weight'] = args['weight']
        
        if args['gender']:
            if not args['gender'] in ['M', 'F']:
                abort(400, {'error': "Gender must be 'M' or 'F'"})
            new_user_data['gender'] = args['gender']
        
        if args['current_level_of_activity']:
            if not args['current_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']:
                abort(400, {'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            new_user_data['current_level_of_activity'] = args['current_level_of_activity']
        
        if args['goal_level_of_activity']:
            if not args['goal_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']:
                abort(400, {'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            new_user_data['goal_level_of_activity'] = args['goal_level_of_activity']
        
        if args['weight_goal']:
            if not args['weight_goal'] in ['lose', 'gain', 'maintain']:
                abort(400, {'error': "Weight goal must be 'lose', 'gain', or 'maintain'"})
            new_user_data['weight_goal'] = args['weight_goal']


        new_user = DBUsers(**new_user_data)

        db.session.add(new_user)
        db.session.commit()
        current_max_id += 1
        
        return {"data": {"username": username}}, 201

    def get(self):
        args = user_get_args.parse_args()
        username = args['username']
        user = DBUsers.query.filter_by(username=username).first()

        if not user:
            abort(404, {'error': 'User not found'})

        user_data = {
            'username': user.username,
            'current_daily_calories': user.current_daily_calories,
            'name': user.name,
            'age': user.age,
            'height': user.height,
            'weight': user.weight,
            'gender': user.gender,
            'current_level_of_activity': user.current_level_of_activity,
            'goal_level_of_activity': user.goal_level_of_activity,
            'weight_goal': user.weight_goal
        }

        return user_data, 200
    
    def put(self):
        args = user_put_args.parse_args()
        username = args['username']
        user = DBUsers.query.filter_by(username=username).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if all(args[key] is None for key in ['daily calories', 'name', 'age', 'height', 'weight', 'gender', 'current_level_of_activity', 'goal_level_of_activity', 'weight_goal']):
            abort(400, {'error': 'At least one field must be provided for update'})

        if args['daily calories']:
            if args['daily calories'] < 0:
                abort(400, {'error': 'Daily calories must be a non-negative integer'})
            user.average_daily_calories = args['daily calories']

        if args['name']:
            user.name = args['name']

        if args['age']:
            if args['age'] < 0:
                abort(400, {'error': 'Age must be a non-negative integer'})
            elif args['age'] > 100:
                abort(400, {'error': 'Age must not be an integer greater than 100'})
            user.age = args['age']

        if args['height']:
            if args['height'] < 0:
                abort(400, {'error': 'Height must be a non-negative integer'})
            user.height = args['height']
        
        if args['weight']:
            if args['weight'] < 0:
                abort(400, {'error': 'Weight must be a non-negative integer'})
            user.weight = args['weight']
        
        if args['gender']:
            if not args['gender'] in ['M', 'F']:
                abort(400, {'error': "Gender must be 'M' or 'F'"})
            user.gender = args['gender']
        
        if args['current_level_of_activity']:
            if not args['current_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']:
                abort(400, {'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            user.current_level_of_activity = args['current_level_of_activity']
        
        if args['goal_level_of_activity']:
            if not args['goal_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']:
                abort(400, {'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            user.goal_level_of_activity = args['goal_level_of_activity']
        
        if args['weight_goal']:
            if not args['weight_goal'] in ['lose', 'gain', 'maintain']:
                abort(400, {'error': "Weight goal must be 'lose', 'gain', or 'maintain'"})
            user.weight_goal = args['weight_goal']

        db.session.commit()
        
        return {'message': 'User information updated successfully'}, 200


recipe_get_args = reqparse.RequestParser()
recipe_get_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
recipe_get_args.add_argument("calories", type=int, help="Number of calories of the food", location='args')
recipe_get_args.add_argument("fat", type=str, help="Total Fat (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("sat_fat", type=str, help="Saturated Fat (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("sugar", type=str, help="Sugar (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("sodium", type=str, help="Sodium (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("protein", type=str, help="Protein (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("carbs", type=str, help="Carbohydrates (PDV): 'high' or 'mid' or 'low'", location='args')
recipe_get_args.add_argument("tags", type=list, help="Tags that must be on the food", location='args')

recipe_put_args = reqparse.RequestParser()
recipe_put_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
recipe_put_args.add_argument("recipe_id", type=int, help="Enter the id of the recipe", location='args', required=True)
recipe_put_args.add_argument("rating", type=int, help="Enter the rating, integer from 0 to 5 inclusive", location='args', required=True)

class Recipe(Resource):
    def get(self):
        args = recipe_get_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        resp = getRecipesWithConfiguration(calories=args['calories'], daily=user.goal_daily_calories,
                                           fat=args['fat'], sat_fat=args['sat_fat'],
                                           sugar=args['sugar'], sodium=args['sodium'], protein=args['protein'],
                                           carbs=args['carbs'], tags=args['tags'])
        
        return resp[:5].to_dict()
    
    def put(self):
        args = recipe_put_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})        

        if args['rating'] in [0, 1, 2, 3, 4, 5]:
            abort(400, {'error': 'Rating not integer in range [0, 5]'})
        
        new_rating = DBRatings(user_id=user.user_id, recipe_id=args['recipe_id'], rating=args['rating'])
        db.session.add(new_rating)
        db.session.commit()
        
        return {"data": {"username": args['username']}}, 201

diet_recommendation_get_args = reqparse.RequestParser()
diet_recommendation_get_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)

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

excercise_get_args = reqparse.RequestParser()
excercise_get_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
excercise_get_args.add_argument("type", type=int, help="Number of calories of the food", location='args')
excercise_get_args.add_argument("body_part", type=str, help="Total Fat (PDV): 'high' or 'mid' or 'low'", location='args')
excercise_get_args.add_argument("equipment", type=str, help="Saturated Fat (PDV): 'high' or 'mid' or 'low'", location='args')
excercise_get_args.add_argument("level", type=str, help="Sugar (PDV): 'high' or 'mid' or 'low'", location='args')

recipe_put_args = reqparse.RequestParser()
recipe_put_args.add_argument("username", type=str, help="Enter Username", location='args', required=True)
recipe_put_args.add_argument("recipe_id", type=int, help="Enter the id of the recipe", location='args', required=True)
recipe_put_args.add_argument("rating", type=int, help="Enter the rating, integer from 0 to 5 inclusive", location='args', required=True)

class Excercise(Resource):
    def get(self):
        args = recipe_get_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        resp = getRecipesWithConfiguration(calories=args['calories'], daily=user.goal_daily_calories,
                                           fat=args['fat'], sat_fat=args['sat fat'],
                                           sugar=args['sugar'], sodium=args['sodium'], protein=args['protein'],
                                           carbs=args['carbs'], tags=args['tags'])
        
        return resp[:5].to_dict()
    
    def put(self):
        args = recipe_put_args.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})        

        if args['rating'] in [0, 1, 2, 3, 4, 5]:
            abort(400, {'error': 'Rating not integer in range [0, 5]'})
        
        new_rating = DBRatings(user_id=user.user_id, recipe_id=args['recipe_id'], rating=args['rating'])
        db.session.add(new_rating)
        db.session.commit()
        
        return {"data": {"username": args['username']}}, 201

    
api.add_resource(Recipe, "/recommend/recipe")
api.add_resource(DietRecommendation, "/recommend/diet")
api.add_resource(User, "/user")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)