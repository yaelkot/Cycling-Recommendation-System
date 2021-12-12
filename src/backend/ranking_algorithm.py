import pandas as pd
from datetime import datetime
from scipy.spatial import distance


def set_date_time_mintues(date):
    date = datetime.strptime(date, '%d-%m-%y %H:%M')
    minute = date.time().minute
    hour = date.time().hour
    return hour * 60 + minute


def set_date_day(date):
    date = datetime.strptime(date, '%d-%m-%y %H:%M')
    return date.timetuple().tm_yday


def set_data(path):
    df = pd.read_csv(path)
    df['StartDay'] = df.apply(lambda d: set_date_day(d['StartTime']), axis=1)
    df['StartMinutes'] = df.apply(lambda d: set_date_time_mintues(d['StartTime']), axis=1)
    return df


def recommend(start, duration, df):
    locations = df[df['StartStationName'] == start]
    day_in_year = datetime.now().timetuple().tm_yday
    time_in_day = datetime.now().timetuple().tm_hour * 60 + datetime.now().timetuple().tm_min
    locations['distance'] = locations.apply(lambda row: distance.euclidean((duration, day_in_year, time_in_day), (
    row.TripDurationinmin, row.StartDay, row.StartMinutes)), axis=1)
    locations = locations[['EndStationName', 'distance', 'TripDurationinmin']]
    locations = locations.sort_values('distance')
    return locations


data = set_data('BikeShare.csv')
recommandations = recommend('Oakland Ave', 5, data)
print(recommandations.head(10))
