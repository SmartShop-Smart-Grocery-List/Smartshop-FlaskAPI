
from flask_restful import Resource, reqparse, fields
from flask import Flask, abort
from app.db.models import User as DBUsers

get_parser = reqparse.RequestParser()
get_parser.add_argument("username", type=str, help="Enter Username", location='args', required=True)

class DietRecommendation(Resource):

    def get(self):
        args = get_parser.parse_args()
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
        loa_labels = [('sedentary', 1.2), ('lightly active', 1.375), ('moderately active', 1.55), ('active', 1.725),
                      ('very active', 1.9)]
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
                    option_abmr = bmr * loa_labels[loa + 1][1]
                    lb_loss = round((option_abmr - abmr) / 500, 1)

                    option[
                        'comment'] = f"Increase level of activity to {loa_labels[loa + 1][0]} to lose {lb_loss} lbs per week."
                    option['goal_daily_calories'] = user.current_daily_calories
                    option['goal_level_of_activity'] = loa_labels[loa + 1][0]
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
                    option_abmr = bmr * loa_labels[loa - 1][1]
                    lb_gain = round((abmr - option_abmr) / 500, 1)

                    option[
                        'comment'] = f"Decrease level of activity to {loa_labels[loa - 1][0]} to gain {lb_gain} lbs per week."
                    option['goal_daily_calories'] = user.current_daily_calories
                    option['goal_level_of_activity'] = loa_labels[loa - 1][0]
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
                option[
                    'comment'] = f"Eat {user.current_daily_calories} calories, and maintain {loa_labels[loa][0]} lifestyle to maintain weight."
                option['goal_daily_calories'] = user.current_daily_calories
                option['goal_level_of_activity'] = user.current_level_of_activity
                recommendation_options['option_1'] = option
