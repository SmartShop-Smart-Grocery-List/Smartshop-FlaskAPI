from flask_restful import Resource, reqparse, fields
from flask import Flask, abort
from app.db.models import User as DBUsers, db

get_parser = reqparse.RequestParser()

class LifestyleScore(Resource):
    def get(self):
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


        return 1, 200

