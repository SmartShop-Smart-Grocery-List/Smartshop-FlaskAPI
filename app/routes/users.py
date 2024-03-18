from flask_restful import Resource, reqparse, fields
from flask import Flask, abort
from app.db.models import User as DBUsers, db

post_parser = reqparse.RequestParser()
get_parser = reqparse.RequestParser()
put_parser = reqparse.RequestParser()

get_parser.add_argument('username', type=str, required=True, help='Username is required', location='args')

post_parser.add_argument('username', type=str, required=True, help='Username is required', location='form')
post_parser.add_argument('current_daily_calories', type=int, help='Enter the current daily calories for this user',
                         location='form')
post_parser.add_argument('goal_daily_calories', type=int, help='Enter the goal daily calories for this user',
                         location='form')
post_parser.add_argument('name', type=str, help='Name of the user', location='form')
post_parser.add_argument('age', type=int, help='Age of the user', location='form')
post_parser.add_argument('height', type=int, help='Height of the user in inches', location='form')
post_parser.add_argument('weight', type=int, help='Weight of the user in lbs', location='form')
post_parser.add_argument('gender', type=str, help="Gender of the user", location='form')
post_parser.add_argument('current_level_of_activity', type=str,
                         help="""Current level of activity: 'sedentary' (little or no exercise), 'lightly active' (exercise 1–3 days/week), 
'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 'very active' (hard exercise 6–7 days/week)]""",
                         location='form')
post_parser.add_argument('goal_level_of_activity', type=str,
                         help="""Goal level of activity: 'sedentary' (little or no exercise), 
'lightly active' (exercise 1–3 days/week), 'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 
'very active' (hard exercise 6–7 days/week)]""", location='form')
post_parser.add_argument('weight_goal', type=str, help="Weight goal: 'lose', 'gain', 'maintain'", location='form')

put_parser.add_argument('username', type=str, required=True, help='Username is required', location='args')
put_parser.add_argument('current_daily_calories', type=int, help='Enter the current daily calories for this user',
                        location='args')
put_parser.add_argument('goal_daily_calories', type=int, help='Enter the goal daily calories for this user',
                        location='form')
put_parser.add_argument('name', type=str, help='Name of the user', location='args')
put_parser.add_argument('age', type=int, help='Age of the user', location='args')
put_parser.add_argument('height', type=int, help='Height of the user in inches', location='args')
put_parser.add_argument('weight', type=int, help='Height of the user in inches', location='args')
put_parser.add_argument('gender', type=str, help="Gender of the user", location='args')
put_parser.add_argument('current_level_of_activity', type=str,
                        help="""Current level of activity: 'sedentary' (little or no exercise), 'lightly active' (exercise 1–3 days/week), 
'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 'very active' (hard exercise 6–7 days/week)]""",
                        location='args')
put_parser.add_argument('goal_level_of_activity', type=str,
                        help="""Goal level of activity: 'sedentary' (little or no exercise), 
'lightly active' (exercise 1–3 days/week), 'moderately active' (exercise 3–5 days/week), 'active' (exercise 6–7 days/week), 
'very active' (hard exercise 6–7 days/week)]""", location='args')
put_parser.add_argument('weight_goal', type=str, help="Weight goal: 'lose', 'gain', 'maintain'", location='args')

user_fields = {
    'username': fields.String,
    'current_daily_calories': fields.Integer,
    'name': fields.String,
    'age': fields.Integer,
    'height': fields.Integer,
    'weight': fields.Float,
    'gender': fields.String,
    'current_level_of_activity': fields.String,
    'goal_level_of_activity': fields.String,
    'weight_goal': fields.String
}


class User(Resource):
    """
    Resource class for managing user data.

    Methods:
        get(self): Retrieves user data.
        post(self): Creates a new user.
        put(self): Updates user information.
    """
    def get(self):
        """
        Retrieves user data.

        Returns:
            Tuple[Dict[str, Any], int]: Tuple containing user data and HTTP status code.
        """

        args = get_parser.parse_args()
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

    def post(self):
        """
        Creates a new user.

        Returns:
            Tuple[Dict[str, str], int]: Tuple containing response data and HTTP status code.
        """
        args = post_parser.parse_args()

        if len(args['username']) > 128:
            abort(400, {'error': 'Username must be 128 characters or less'})

        username = args['username']
        user = DBUsers.query.filter_by(username=username).first()

        if user:
            abort(403, {'error': 'User already exists'})

        global current_max_id
        if current_max_id is None:
            current_max_id = db.session.query(db.func.max(DBUsers.user_id)).scalar() or 60315

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
            new_user_data['gender'] = args['gender']

        if args['current_level_of_activity']:
            if not args['current_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active',
                                                         'very active']:
                abort(400, {
                    'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            new_user_data['current_level_of_activity'] = args['current_level_of_activity']

        if args['goal_level_of_activity']:
            if not args['goal_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active',
                                                      'very active']:
                abort(400, {
                    'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
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

    def put(self):
        """
        Updates user information.

        Returns:
            Tuple[Dict[str, str], int]: Tuple containing response message and HTTP status code.
        """
        args = put_parser.parse_args()
        username = args['username']
        user = DBUsers.query.filter_by(username=username).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if all(args[key] is None for key in
               ['daily calories', 'name', 'age', 'height', 'weight', 'gender', 'current_level_of_activity',
                'goal_level_of_activity', 'weight_goal']):
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
            user.gender = args['gender']

        if args['current_level_of_activity']:
            if not args['current_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active',
                                                         'very active']:
                abort(400, {
                    'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            user.current_level_of_activity = args['current_level_of_activity']

        if args['goal_level_of_activity']:
            if not args['goal_level_of_activity'] in ['sedentary', 'lightly active', 'moderately active', 'active',
                                                      'very active']:
                abort(400, {
                    'error': "Level of activity must be ['sedentary', 'lightly active', 'moderately active', 'active', 'very active']"})
            user.goal_level_of_activity = args['goal_level_of_activity']

        if args['weight_goal']:
            if not args['weight_goal'] in ['lose', 'gain', 'maintain']:
                abort(400, {'error': "Weight goal must be 'lose', 'gain', or 'maintain'"})
            user.weight_goal = args['weight_goal']

        db.session.commit()

        return {'message': 'User information updated successfully'}, 200
