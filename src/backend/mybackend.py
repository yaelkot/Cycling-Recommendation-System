import sqlite3
import pandas as pd
import numpy as np
from scipy.spatial import distance
from datetime import datetime, timedelta

seasons = {'0': [1, 2, 3], '1': [4, 5, 6], '2': [7, 8, 9], '3': [10, 11, 12]}


class Database:

    def __init__(self, csv):
        """

        :param csv: path to the csv_file with the data for the system
        :raise TyepError: raise type error if csv is not string
        :raise ValuError: raise value error if csv is path to csv file
        constructor for the mybackend class
        """
        if type(csv) != str:
            raise TypeError("csv must be string")
        if not csv.endswith(".csv"):
            raise ValueError("csv must be path csv file")
        self.db = self.create_data_table_and_insert_data(csv)

    def create_data_table_and_insert_data(self, data):
        """
        :param rows:
        :return: path to the created database
        method for reading the csv file that passed in the constructor,
        and creating database if not exist and insert the data in the csv
        to the data table in the database, and also manipulate the data
        to create the relevant data for make the recommendation for the users
        """
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
        """
        :param rows:
        :return:
        method that insert the relevant data for the recommendations
        into the RankData table in the database
        """
        conn = sqlite3.connect('database2.db')
        cur = conn.cursor()
        query1 = """CREATE TABLE IF NOT EXISTS RankData 
                (StartStationName TEXT, EndStationName TEXT, StartTime Text, StartDayPart INTEGER, 
                TripSeason INTEGER, TripDurationinmin INTEGER, TripDurationCategory Integer, 
                StartDayInYear INTEGER, StartMinute INTEGER)"""
        query2 = 'INSERT INTO RankData values (?,?,?,?,?,?,?,?,?)'
        cur.execute(query1)
        cur.executemany(query2, rows)
        conn.commit()
        conn.close()

    def get_places(self, start_station, time_duration, k):
        """
        :param start_station: the start station of the user
        :param time_duration: duration of time the users wants to ride
        :param k: number of recommendations the user want to recive
        :raise ValueError: throws value error if k or time_duration are not a number
        :raise TypeError: throws type error if one or more parameter are not string
        :return: list of the places that recommended to the user
        the function gets the user input and select the relevant trips
        according to the start station from the database, and use the most similar trip
        method to calculate the most similar trip for each possible end station
        and return the results of this calculation
        """
        if not time_duration.isdigit():
            raise ValueError("time duration must be a positive number")
        if not k.isdigit():
            raise ValueError("k(number of recommendations) duration must be a positive number")
        if type(start_station) != str or type(time_duration) != str or type(k) != str:
            raise TypeError("The input for the method must be string")
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cat = self.set_trip_category(int(time_duration))
        query1 = "SELECT * FROM RankData WHERE StartStationName=? AND TripDurationCategory=?"
        result = cur.execute(query1, (start_station, cat)).fetchall()
        dataframe = pd.DataFrame(result, columns=['StartStationName', 'EndStationName',
                                                  'StartTime', 'StartDayPart',
                                                  'TripSeason', 'TripDurationinmin',
                                                  'TripDurationCategory', 'StartDayInYear', 'StartMinute'])
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
        """
        :param duration: the ride duration was given as input by the user
        :param dur_cat: the category of trip, calaulated in the get places method
        :return: numpy array with all the parameters necessary to calculate the
        recommendations
         the method get the current time, and calculate the date and the hour
         and also categorize them and return array with the parameters required
         for recommendations calculation
        """
        time = datetime.now()
        time = str(time.strftime('%d-%m-%y %H:%M'))
        start_time_data = self.calculate_date_data(time)
        dur = int(duration)
        return np.array(start_time_data + [dur])

    def calculate_date_data(self, date):
        """
        :param date: the current datetime
        :return: list with the relevant data about the date time
        the method get all the data from the date that relevant for calculating
        the recommendations
        """
        day_struct = datetime.strptime(str(date), '%d-%m-%y %H:%M').timetuple()
        season = self.set_season(date)
        day_part = self.set_day_part(date)
        start_year_day = day_struct.tm_yday
        min_of_day = day_struct.tm_hour * 60 + day_struct.tm_min
        return [season, day_part, start_year_day, min_of_day]

    def get_most_similar_trip(self, input_vector, df):
        """
        :param input_vector: numpy array with the relevant data for calculate similarity between trips
        :param df: dataframe with data about trips that matches user input
        :return: return the most similar trip from the input dataframe
        the method first calculate hamming distance between 2 of the parameters of the
        to the TripSeason and the TripDayPart in order to filter the trips that are most similar to the
        user input, and after that calculates cosin similarity between the user input and the remaining
        trips and returns the that got the highest result after the similarity calculation
        """
        print(input_vector)
        df['distance'] = df.apply(lambda row: distance.hamming(input_vector[:2], np.array([row['TripSeason'], row['StartDayPart']],)), axis=1)
        min_dist = min(set(df['distance'].tolist()))
        most_sim_places = df[df['distance'] == min_dist]
        most_sim_places['similarity'] = most_sim_places.apply(
            lambda row: 1 - distance.cosine(input_vector[2:], np.array([
                row['StartDayInYear'], row['StartMinute'], row['TripDurationinmin']
            ]), [0.3, 0.2, 0.5]), axis=1)
        res = most_sim_places.loc[most_sim_places['similarity'].idxmax()]
        res = res[['EndStationName', 'TripDurationinmin', 'StartTime', 'similarity']]
        return res

    def create_extended_start_time(self, data):
        """
        :param data: the data from the csv file was given as input to the constructor
        :return: 2d list that every input list contains relevant data for the recommendations calcuation
        The method run on every row in the data, and create new list with the data about the trip time
        and add it to the result list
        """
        result = []
        for i in data:
            time_tuple_start = datetime.strptime(i[1], '%d-%m-%y %H:%M').timetuple()
            time_tuple_end = datetime.strptime(i[2], '%d-%m-%y %H:%M').timetuple()
            row = []
            row.append(i[4])  # start station
            row.append(i[8])  # end station
            row.append(i[1])  # start time
            row.append(self.set_day_part(i[1]))  # start time part of the day # start time day in the week
            row.append(self.set_season(i[1]))  # start time season
            row.append(int(i[15]))  # duration in minutes
            row.append(self.set_trip_category(int(i[15])))  # duration in categories
            row.append(time_tuple_start.tm_yday)  # start time day in the year
            row.append(time_tuple_start.tm_hour * 60  # start time minute in the day
                       + time_tuple_start.tm_min)
            result.append(row)
        return result

    def set_trip_category(self, duration):
        """
        :param duration: time duration of a trip
        :return: the category of the trip, number between 1 to 31
        the method consider every 5 minutes as category if the duration is less than 100
        minutes, 100 minutes if the duration between 100 minutes to 1000 minutes, and
        if the duration is more than 1000 minutes, the trip get category 31
        """
        if duration < 100:
            return int(int(duration) / 5) + 1
        elif 100 <= duration <= 1000:
            return 20 + int(int(duration) / 100) + 1
        else:
            return 31

    def set_day_part(self, date):
        """
        :param date: the date of the trip
        :return: number between 0 to 3
        the method give to trip category according the hour the trip occured,
        every 6 days considered as category
        """
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
        """
        :param date: the date of the trip
        :return: the category of trip according the season of this date
        the method categorize the trip according to season by the month the trip
        occured, which is classified to season in the season dictionary in the top of
        the file
        """
        date = datetime.strptime(date, '%d-%m-%y %H:%M')
        mon = date.timetuple().tm_mon
        for i in seasons:
            if int(mon) in seasons[i]:
                return int(i)

