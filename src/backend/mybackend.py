import sqlite3
import pandas as pd
import numpy as np
from scipy.spatial import distance
from datetime import datetime

seasons = {'0': [1, 2, 3], '1': [4, 5, 6], '2': [7, 8, 9], '3': [10, 11, 12]}


class Database:

    def __init__(self, csv):
        self.db = self.create_data_table_and_insert_data(csv)

    def create_data_table_and_insert_data(self, data):
        conn = sqlite3.connect('database2.db')
        rows = []
        cur = conn.cursor()
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data' ''')
        if cur.fetchone()[0] == 0:
            with open(data, 'r') as cv:
                lines = cv.readlines()
                rows = lines[1:]
            rows = list(map(lambda s: s.split(','), rows))
            ranker_data = self.create_extended_start_time(rows)
            query = """CREATE TABLE IF NOT EXISTS data 
                    (TripDuration INTEGER, StartTime TEXT, StopTime TEXT, StartStationID INTEGER,
                    StartStationName TEXT, StartStationLatitude REAL, StartStationLongitude REAL,
                    EndStationID INTEGER, EndStationName TEXT, EndStationLatitude REAL, EndStationLongitude REAL, 
                    BikeID INTEGER, UserType TEXT, BirthYear INTEGER, Gender INTEGER, TripDurationinmin INTEGER)"""
            query2 = 'INSERT INTO data values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            cur.execute(query)
            conn.commit()
            cur.executemany(query2, rows)
            conn.commit()
            conn.close()
            self.create_rank_data(ranker_data)
        return 'database2.db'

    def create_rank_data(self, rows):
        conn = sqlite3.connect('database2.db')
        cur = conn.cursor()
        query1 = """CREATE TABLE IF NOT EXISTS RankData 
                (StartStationName TEXT, EndStationName TEXT, StartTime Text, StartDayPart INTEGER, TripWeekDay INTEGER, 
                TripSeason INTEGER, TripDurationinmin INTEGER, TripDurationCategory Integer, 
                StartDayInYear INTEGER, StartMinute INTEGER )"""
        query2 = 'INSERT INTO RankData values (?,?,?,?,?,?,?,?,?,?)'
        cur.execute(query1)
        cur.executemany(query2, rows)
        conn.commit()
        conn.close()

    def get_places(self, start_station, time_duration, k):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        query1 = "SELECT * FROM RankData WHERE StartStationName=?"
        result = cur.execute(query1, (start_station,)).fetchall()
        dataframe = pd.DataFrame(result, columns=['StartStationName', 'EndStationName',
                                                  'StartTime', 'StartDayPart',
                                                  'TripWeekDay', 'TripSeason', 'TripDurationinmin',
                                                  'TripDurationCategory', 'StartDayInYear', 'StartMinute'])
        print(dataframe)
        curr_day = str(datetime.now().strftime('%d-%m-%y %H:%M'))
        all_places = set(dataframe['EndStationName'].tolist())
        print(len(all_places))
        in_vector = self.create_input_vector(curr_day, time_duration)
        recommends = pd.DataFrame(columns=['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity'])
        for i in all_places:
            max_place_i = self.get_most_similar_trip(in_vector, dataframe[dataframe['EndStationName'] == i])
            recommends = pd.concat([recommends, max_place_i.to_frame().T])
        recommends = recommends.sort_values(by=['similarity'], ascending=[False])
        print(recommends.head(int(k)))
        return recommends.head(int(k))['EndStationName'].tolist()

    def create_input_vector(self, day, duration):
        day_struct = datetime.strptime(day, '%d-%m-%y %H:%M').timetuple()
        category = int(int(duration) / 5) + 1
        season = self.set_season(day)
        week_day = day_struct.tm_wday
        day_part = self.set_day_part(day)
        year_day = day_struct.tm_yday
        min_of_day = day_struct.tm_hour * 60 + day_struct.tm_min
        dur = int(duration)
        return np.array([category, season, week_day, day_part, year_day, min_of_day, dur])

    def get_most_similar_trip(self, input_vector, df):
        df['distance'] = df.apply(lambda row: distance.hamming(input_vector[:4], np.array(
            [row['TripDurationCategory'], row['TripSeason'], row['TripWeekDay'], row['StartDayPart']]),
                                                               np.array([0.4, 0.2, 0.1, 0.2])), axis=1)
        min_dist = min(set(df['distance'].tolist()))
        most_sim_places = df[df['distance'] == min_dist]
        most_sim_places['similarity'] = most_sim_places.apply(
            lambda row: 1 - distance.cosine(input_vector[4:], np.array([
                row['StartDayInYear'], row['StartMinute'], row['TripDurationinmin']
            ]), [0.15, 0.35, 0.5]), axis=1)
        res = most_sim_places.loc[most_sim_places['similarity'].idxmax()]
        res = res[['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity']]
        return res

    def create_extended_start_time(self, data):
        result = []
        for i in data:
            time_tuple = datetime.strptime(i[1], '%d-%m-%y %H:%M').timetuple()
            row = []
            row.append(i[4]) #start station
            row.append(i[8]) #end station
            row.append(i[1]) #start time
            row.append(self.set_day_part(i[1]))#start time part of the day
            row.append(time_tuple.tm_wday) #start time day in the week
            row.append(self.set_season(i[1])) #start time season
            row.append(int(i[15])) #duration in minutes
            row.append(int(int(i[15]) / 5) + 1) #duration in categories
            row.append(time_tuple.tm_yday) #start time day in the year
            row.append(time_tuple.tm_hour * 60 #start time minute in the day
                       + time_tuple.tm_min)
            result.append(row)
        return result

    def set_day_part(self, date):
        date = datetime.strptime(date, '%d-%m-%y %H:%M')
        minute = date.time().minute
        day_minute = date.time().hour * 60 + minute
        if 0 <= day_minute <= 360:
            return 0
        elif 360 < day_minute <= 720:
            return 1
        elif 720 < day_minute <= 1080:
            return 2
        else:
            return 3

    def set_season(self, date):
        date = datetime.strptime(date, '%d-%m-%y %H:%M')
        mon = date.timetuple().tm_mon
        for i in seasons:
            if int(mon) in seasons[i]:
                return int(i)
