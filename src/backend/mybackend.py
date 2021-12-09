import sqlite3


class Database:

    def __init__(self, csv):
        self.db = self.create_data_table_and_insert_data(csv)

    def create_data_table_and_insert_data(self, data):
        query1 = 'CREATE TABLE IF NOT EXISTS data ()'
        rows = []
        with open(data) as cv:
            lines = cv.readlines()
            rows = lines[1:]
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS data ()')
        return 'database.db'

db = Database('BikeShare.csv')