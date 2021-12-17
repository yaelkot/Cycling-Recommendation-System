import sqlite3
import pandas as pd
import numpy as np
from scipy.spatial import distance
from datetime import datetime, timedelta

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
                StartDayInYear INTEGER, StartMinute INTEGER, StopTime TEXT, StopDayPart INTEGER, StopWeekday INTEGER,
                StopSeason INTEGER, StopDayInYear INTEGER, StopMinute INTEGER)"""
        query2 = 'INSERT INTO RankData values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        cur.execute(query1)
        cur.executemany(query2, rows)
        conn.commit()
        conn.close()

    def get_places(self, start_station, time_duration, k):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cat = self.set_trip_category(int(time_duration))
        query1 = "SELECT * FROM RankData WHERE StartStationName=? AND TripDurationCategory=?"
        result = cur.execute(query1, (start_station, cat)).fetchall()
        dataframe = pd.DataFrame(result, columns=['StartStationName', 'EndStationName',
                                                  'StartTime', 'StartDayPart',
                                                  'TripWeekDay', 'TripSeason', 'TripDurationinmin',
                                                  'TripDurationCategory', 'StartDayInYear', 'StartMinute',
                                                  'StopTime', 'StopDayPart', 'StopWeekday', 'StopSeason',
                                                  'StopDayInYear', 'StopMinute'])
        all_places = set(dataframe['EndStationName'].tolist())
        in_vectors = self.create_input_vector(time_duration, cat)
        recommends = pd.DataFrame(columns=['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity'])
        for i in all_places:
            max_place_i = self.get_most_similar_trip(in_vectors, dataframe[dataframe['EndStationName'] == i])
            recommends = pd.concat([recommends, max_place_i.to_frame().T])
        recommends = recommends.sort_values(by=['similarity'], ascending=[False])
        print(recommends.head(int(k)))
        return recommends.head(int(k))['EndStationName'].tolist()

    def create_input_vector(self, duration, dur_cat):
        time = datetime.now()
        end_time = self.calculate_end_time(duration, time)
        time = str(time.strftime('%d-%m-%y %H:%M'))
        start_time_data = self.calculate_date_data(time)
        end_time_data = self.calculate_date_data(end_time)
        dur = int(duration)
        return np.array([dur_cat] + start_time_data[0] + end_time_data[0]), np.array([dur] + start_time_data[1] + end_time_data[1])

    def calculate_date_data(self, date):
        day_struct = datetime.strptime(str(date), '%d-%m-%y %H:%M').timetuple()
        season = self.set_season(date)
        week_day = day_struct.tm_wday
        day_part = self.set_day_part(date)
        start_year_day = day_struct.tm_yday
        min_of_day = day_struct.tm_hour * 60 + day_struct.tm_min
        return [season, week_day, day_part], [start_year_day, min_of_day]

    def get_most_similar_trip(self, input_vector, df):
        in_vec1 = np.concatenate((np.array([input_vector[0][1]]), np.array([input_vector[0][3]])))
        in_vec2 = np.array([input_vector[1][0], input_vector[1][2]])
        df['distance'] = df.apply(lambda row: distance.hamming(in_vec1, np.array([row['TripSeason'], row['StartDayPart']],)), axis=1)
        min_dist = min(set(df['distance'].tolist()))
        most_sim_places = df[df['distance'] == min_dist]
        most_sim_places['similarity'] = most_sim_places.apply(
            lambda row: 1 - distance.cosine(input_vector[1][:3], np.array([
                row['TripDurationinmin'], row['StartDayInYear'], row['StartMinute']
            ]), [0.5, 0.2, 0.3]), axis=1)
        res = most_sim_places.loc[most_sim_places['similarity'].idxmax()]
        res = res[['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity']]
        return res

    def create_extended_start_time(self, data):
        result = []
        for i in data:
            time_tuple_start = datetime.strptime(i[1], '%d-%m-%y %H:%M').timetuple()
            time_tuple_end = datetime.strptime(i[2], '%d-%m-%y %H:%M').timetuple()
            row = []
            row.append(i[4])  # start station
            row.append(i[8])  # end station
            row.append(i[1])  # start time
            row.append(self.set_day_part(i[1]))  # start time part of the day
            row.append(time_tuple_start.tm_wday)  # start time day in the week
            row.append(self.set_season(i[1]))  # start time season
            row.append(int(i[15]))  # duration in minutes
            row.append(self.set_trip_category(int(i[15])))  # duration in categories
            row.append(time_tuple_start.tm_yday)  # start time day in the year
            row.append(time_tuple_start.tm_hour * 60  # start time minute in the day
                       + time_tuple_start.tm_min)
            row.append(i[2])
            row.append(self.set_day_part(i[2]))
            row.append(time_tuple_end.tm_wday)  # start time day in the week
            row.append(self.set_season(i[2]))  # start time season
            row.append(time_tuple_end.tm_yday)
            row.append(time_tuple_end.tm_hour * 60  # start time minute in the day
                       + time_tuple_end.tm_min)
            result.append(row)
        return result

    def set_trip_category(self, duration):
        if duration < 100:
            return int(int(duration) / 5) + 1
        elif 100 <= duration <= 1000:
            return 20 + int(int(duration) / 100) + 1
        else:
            return 31

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

    def calculate_end_time(self, duration, curr_date):
        time_delta = timedelta(minutes=int(duration))
        future_time = datetime.strftime(curr_date + time_delta, '%d-%m-%y %H:%M')
        return future_time
