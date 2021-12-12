import sqlite3

class Database:

    def __init__(self, csv):
        self.db = self.create_data_table_and_insert_data(csv)

    def create_data_table_and_insert_data(self, data):
        conn = sqlite3.connect('database.db')
        rows = []
        cur = conn.cursor()
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data' ''')
        if cur.fetchone()[0] == 0:
            with open(data, 'r') as cv:
                lines = cv.readlines()
                rows = lines[1:]
            rows = map(lambda s: s.split(','), rows)
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
        return 'database.db'

    def get_places(self, start_station, time_duration, k):
        conn = sqlite3.connect(self.db)
        query = "SELECT EndStationName FROM data WHERE StartStationName=? AND TripDurationinmin=? LIMIT ?"
        cur = conn.cursor()
        cur.execute(query, (start_station, time_duration, k))
        res = cur.fetchall()
        res = list(map(lambda t: t[0], res))
        return res

