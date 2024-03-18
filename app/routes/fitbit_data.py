from flask import current_app as app, request, abort
from flask_restful import reqparse, Resource
from app.external.fitbit import authenticate, setup_database, archive_data

post_parser = reqparse.RequestParser()
post_parser.add_argument('access_token', type=str, required=True)
post_parser.add_argument('refresh_token', type=str, required=True)
args = post_parser.parse_args()


class FitbitData(Resource):
    def post(self):
        args = post_parser.parse_args()
        access_token = args['access_token']
        refresh_token = args['refresh_token']

        authenticate(access_token, refresh_token)

        try:
            archive_data()
            setup_database()
        except Exception as e:
            abort(404, {'error': {str(e)}})

        return {'message': 'Data fetched successfully'}, 201
