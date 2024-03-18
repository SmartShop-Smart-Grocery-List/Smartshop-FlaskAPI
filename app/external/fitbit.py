import fitbit
import datetime
import os
import sqlite3
import pandas as pd
from flask import current_app
from app.db.models import db, FitBit

CLIENT_ID = current_app.config["CLIENT_ID"]
CLIENT_SECRET = current_app.config["CLIENT_SECRET"]
HOME = os.path.join(os.getcwd())


def authenticate(ACCESS_TOKEN, REFRESH_TOKEN):
    global auth2_client
    auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN,
                                 refresh_token=REFRESH_TOKEN)


def fetchDistance():
    today = datetime.date.today()
    prev_week = today - datetime.timedelta(weeks=1)
    distance_json = auth2_client.time_series('activities/distance', base_date=prev_week, end_date=today)
    lines = []
    outfile = open("1_distance_data.csv", 'w')
    for object in distance_json['activities-distance']:
        dateTime = object['dateTime']
        value = object['value']
        format = f"{dateTime}, {round(float(value), 2)}\n"
        lines.append(format)
    outfile.writelines(lines)
    outfile.close()


def fetchSteps():
    today = datetime.date.today()
    prev_week = today - datetime.timedelta(weeks=1)
    steps_json = auth2_client.time_series('activities/steps', base_date=prev_week, end_date=today)
    lines = []
    outfile = open("2_steps_data.csv", 'w')
    for object in steps_json['activities-steps']:
        value = object['value']
        format = f"{value}\n"
        lines.append(format)
    outfile.writelines(lines)
    outfile.close()


def fetchSleep():
    today = datetime.date.today()
    prev_week = today - datetime.timedelta(weeks=1)
    sleep_json = auth2_client.time_series('sleep/', base_date=prev_week, end_date=today)
    lines = []
    outfile = open("3_sleep_data.csv", 'w')
    for object in sleep_json['sleep']:
        minutesAsleep = object['minutesAsleep'] / 60
        format = f"{round(float(minutesAsleep), 2)}\n"
        lines.append(format)
    outfile.writelines(lines)
    outfile.close()


def fetchCaloriesBurned():
    today = datetime.date.today()
    prev_week = today - datetime.timedelta(weeks=1)
    calories_json = auth2_client.time_series('activities/calories', base_date=prev_week, end_date=today)
    lines = []
    outfile = open("4_calories_data.csv", 'w')
    for object in calories_json['activities-calories']:
        value = object['value']
        format = f"{value}\n"
        lines.append(format)
    outfile.writelines(lines)
    outfile.close()


def fetchHeartRate():
    today = datetime.date.today()
    prev_week = today - datetime.timedelta(weeks=1)
    heart_json = auth2_client.time_series('activities/heart', base_date=prev_week, end_date=today)
    lines = []
    outfile = open("5_hr_data.csv", 'w')
    for object in heart_json['activities-heart']:
        if 'restingHeartRate' in object['value']:
            maxHeartRate = object['value']['heartRateZones'][1]['max']
            restingHeartRate = object['value']['restingHeartRate']
            format = f"{maxHeartRate}, {restingHeartRate}\n"
            lines.append(format)
    outfile.writelines(lines)
    outfile.close()


def mergeCSV():
    csv_files = os.listdir(os.getcwd())

    df1 = 0
    df2 = 0
    df3 = 0
    df4 = 0
    df5 = 0

    for index in range(len(csv_files)):
        try:
            if index == 0:
                df1 = pd.read_csv(csv_files[index])
            elif index == 1:
                df2 = pd.read_csv(csv_files[index])
            elif index == 2:
                df3 = pd.read_csv(csv_files[index])
            elif index == 3:
                df4 = pd.read_csv(csv_files[index])
            else:
                df5 = pd.read_csv(csv_files[index])
        except:
            old_files = os.listdir(os.chdir('../Week 3'))
            if index == 0:
                df1 = pd.read_csv(old_files[index])
            elif index == 1:
                df2 = pd.read_csv(old_files[index])
            elif index == 2:
                df3 = pd.read_csv(old_files[index])
            elif index == 3:
                df4 = pd.read_csv(old_files[index])
            else:
                df5 = pd.read_csv(old_files[index])

            os.chdir('../../..')
            os.chdir(os.listdir(os.getcwd())[-1])

    merged = pd.concat([df1, df2, df3, df4, df5], axis=1)

    outfile = open("health_data.csv", 'w')
    merged.to_csv('health_data.csv', index=False)
    outfile.close()


def load_index():
    index_path = os.path.join(HOME, 'index')

    if not os.path.exists(index_path):  # index directory does not exist
        os.makedirs(index_path)  # create index directory

    os.chdir(index_path)  # change cwd to index

    dir_list = os.listdir(index_path)  # update cwd

    if not dir_list:  # list dirs in index
        os.makedirs('Week 1')  # if no dirs exist, create the first one
    else:
        last_dir = max(dir_list, key=lambda x: int(x.split(' ')[-1]))
        last_index = int(last_dir.split(' ')[-1])
        next_index = last_index + 1
        next_dir_name = f'Week {next_index}'
        os.makedirs(next_dir_name)

    os.chdir(next_dir_name)


def setup_database():
    os.chdir(f'{HOME}/assets')

    # Close the database connection if it's open
    conn = None
    cursor = None

    try:
        db.session.query(FitBit).delete()
        db.session.commit()

        os.chdir(f'{HOME}/model/data')
        dir = os.listdir(os.getcwd())[-1]
        os.chdir(dir)

        df = pd.read_csv('health_data.csv', header=None)
        df.columns = ['date', 'distance', 'steps', 'sleep', 'calories', 'restingHeartRate', 'maxHeartRate']
        df.to_sql(name='fitbit_data', con=db, if_exists='append', index=False)
        db.session.commit()

    except Exception as e:
        print(f"Error setting up database: {e}")

    # Rename the file outside of the try-except-finally block
    os.chdir(f'{HOME}/model/data')


def archive_data():
    load_index()
    fetchDistance()
    fetchSteps()
    fetchSleep()
    fetchCaloriesBurned()
    fetchHeartRate()
    mergeCSV()
