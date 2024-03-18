from flask_restful import Resource, reqparse, fields
from flask import Flask, abort
from app.db.models import User as DBUsers, db, FitBit
from model.contextualization.context import Context
from model.personalization.personalization import Personalizer
from model.recommendation.recommend import Recommender

get_parser = reqparse.RequestParser()
get_parser.add_argument('user', type=str, location='args')


class LifestyleScore(Resource):
    """
    Resource class for calculating lifestyle scores.

    Methods:
        get(self): Retrieves lifestyle score for a user.
    """

    def get(self):
        """
        Retrieves lifestyle score for a user.

        Returns:
            Tuple: Tuple containing the lifestyle score and HTTP status code.
        """
        args = get_parser.parse_args()
        print(args['user'])
        user = db.session.query(DBUsers).where(DBUsers.username == args['user']).first()
        userData = lambda r: {c.name: str(getattr(r, c.name)) for c in user.__table__.columns}
        if not user:
            abort(404, {'error': 'User not found'})

        fit_data = db.session.query(FitBit).where(FitBit.user_id == user.user_id).all()

        fd = [dir(data) for data in fit_data]
        userinfo = userData(user)

        personalized = Personalizer(userinfo, fd)
        recommender = Recommender(context=None, personalizer=personalized)

        return recommender.get_lifestyle_score()
