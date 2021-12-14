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
                TripSeason INTEGER, TripDurationinmin INTEGER, TripDurationCategory Integer)"""
        query2 = 'INSERT INTO RankData values (?,?,?,?,?,?,?,?)'
        cur.execute(query1)
        cur.executemany(query2, rows)
        conn.commit()
        conn.close()

    def get_places(self, start_station, time_duration, k):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        query1 = "SELECT * FROM RankData WHERE StartStationName=?"
        result = cur.execute(query1, (start_station,))
        dataframe = pd.DataFrame(result, columns=['StartStationName', 'EndStationName',
                                                  'StartTime', 'StartDayPart',
                                                  'TripWeekDay', 'TripSeason', 'TripDurationinmin',
                                                  'TripDurationCategory'])
        curr_day = str(datetime.now().strftime('%d-%m-%y %H:%M'))
        all_places = set(dataframe['EndStationName'].tolist())
        in_vector = np.array([(int(time_duration/5)) + 1, self.set_season(curr_day),
                              datetime.strptime(curr_day, '%d-%m-%y %H:%M').timetuple().tm_wday,
                              self.set_day_part(curr_day)])
        for i in all_places:
            max_place_i = self.get_most_similar_trip(in_vector, dataframe[dataframe['EndStationName'] == i])
            result = pd.concat([result, max_place_i.to_frame().T])
        result = result.sort_values(by=['similarity'], ascending=[True])
        return result.head(k)['EndStationName']

    def get_most_similar_trip(self,input_vector, df):
        df['similarity'] = df.apply(lambda row: distance.hamming(input_vector, np.array(
            [row['TripDurationCategory'], row['TripSeason'], row['TripDay'], row['TripDayPart']]),
                                                                 np.array([0.5, 0.1, 0.1, 0.2])), axis=1)
        res = df.loc[df['similarity'].idxmin()]
        res = res[['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity']]
        return res

    def create_extended_start_time(self, data):
        result = []
        for i in data:
            row = []
            row.append(i[4])
            row.append(i[8])
            row.append(i[2])
            row.append(self.set_day_part(i[1]))
            row.append(datetime.strptime(i[1], '%d-%m-%y %H:%M').timetuple().tm_wday)
            row.append(self.set_season(i[1]))
            row.append(int(i[15]))
            row.append(int(int(i[15])/5) + 1)
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



