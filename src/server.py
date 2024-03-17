from flask import Flask, request
from src import main

app = Flask(__name__)
    
@app.route("/fitbitdata", methods=['POST'])
def fetch_data():
    access_token = request.form.get('access_token')
    refresh_token = request.form.get('refresh_token')

    main.authenticate(access_token, refresh_token)
    
    try: 
        main.archive_data()
        main.setup_database()
        return 'Data fetched successfully!'
    except Exception as e:
        return f'Error fetching data: {str(e)}'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)