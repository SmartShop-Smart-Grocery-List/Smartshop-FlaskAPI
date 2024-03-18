from flask_restful import Resource, reqparse
from flask import abort
from app.db.models import User as DBUsers, ExerciseRating as DBExerciseRatings, db
from model.preprocessing import preprocess
from model.recommendation.recommend import Recommender

get_parser = reqparse.RequestParser()
get_parser.add_argument("username", type=str, help="Enter Username", location='args', required=True)
get_parser.add_argument("type", type=int, help="Enter the type of exercise", location='args')
get_parser.add_argument("body_part", type=str, help="Enter the main body part the exercise is for",
                        location='args')
get_parser.add_argument("equipment", type=str, help="Enter the equipment used in the exercise", location='args')
get_parser.add_argument("level", type=str, help="Enter the difficulty level", location='args')

put_parser = reqparse.RequestParser()
put_parser.add_argument("username", type=str, help="Enter Username", location='args', required=True)
put_parser.add_argument("exercise_id", type=int, help="Enter the id of the exercise", location='args',
                        required=True)
put_parser.add_argument("rating", type=int, help="Enter the rating, integer from 0 to 5 inclusive",
                        location='args', required=True)


class Exercise(Resource):
    def get(self):
        args = get_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        resp = Recommender().get_exercise_with_configuration(exercises=preprocess.data.exercises,
                                                             colab_filter=preprocess.data.exercise_colab_filter,
                                                             type=args['type'],
                                                             body_part=args['body_part'],
                                                             equipment=args['equipment'],
                                                             level=args['level'])

        # return resp[:5].to_dict()
        return {}, 200

    def put(self):
        args = put_parser.parse_args()
        user = DBUsers.query.filter_by(username=args['username']).first()

        if not user:
            abort(404, {'error': 'User not found'})

        if not args['rating'] in [0, 1, 2, 3, 4, 5]:
            abort(400, {'error': 'Rating not integer in range [0, 5]'})

        # TODO
        if not args['exercise_id'] in data_management.data.exercises['id'].values:
            abort(404, {'error': 'Invalid exercise_id'})

        new_rating = DBExerciseRatings(user_id=user.user_id, exercise_id=args['exercise_id'], rating=args['rating'])
        db.session.add(new_rating)
        db.session.commit()

        return {"data": {"username": args['username']}}, 201
