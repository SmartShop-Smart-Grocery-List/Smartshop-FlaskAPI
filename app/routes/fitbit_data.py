from flask import abort
from flask_restful import reqparse, Resource
# from external.fitbit import authenticate, setup_database, archive_data

# # Parser for POST requests
# post_parser = reqparse.RequestParser()
# post_parser.add_argument('access_token', type=str, required=True)
# post_parser.add_argument('refresh_token', type=str, required=True)

# class FitbitData(Resource):


    # def post(self):
    #     model.data.

    # def post(self):
    #     """
    #     Fetches Fitbit data and updates the database.
    #
    #     Returns:
    #         Tuple: Tuple containing acknowledgment message and HTTP status code.
    #     """
    #     args = post_parser.parse_args()
    #     access_token = args['access_token']
    #     refresh_token = args['refresh_token']
    #
    #     authenticate(access_token, refresh_token)
    #
    #     try:
    #         archive_data()
    #         setup_database()
    #     except Exception as e:
    #         abort(404, {'error': {str(e)}})
    #
    #     return {'message': 'Data fetched successfully'}, 201