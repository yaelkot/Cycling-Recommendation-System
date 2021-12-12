import statistics as stat
import pandas as pd
import matplotlib as plt

df = pd.read_csv("BikeShare.csv")

#statistices details of column BirthYear
# earliest_year = df["BirthYear"].min()
# latest_year = df["BirthYear"].max()
# ave_year = stat.mean(df["BirthYear"])
# med_year = stat.median(df["BirthYear"])

# print("earliest year: ", earliest_year)
# print("latest year: ", latest_year)
# print("ave year: ", ave_year)
# print("med year: ", med_year)


#statistices details of column TripDurationinmin
# earliest_time = df["TripDurationinmin"].min()
# latest_time = df["TripDurationinmin"].max()
# ave_time = stat.mean(df["TripDurationinmin"])
# med_time = stat.median(df["TripDurationinmin"])

# print("\nearliest time: ", earliest_time)
# print("latest time: ", latest_time)
# print("ave time: ", ave_time)
# print("med time: ", med_time)


#statistices on category_df
#young
# young_short_bike = df.loc[(df["BirthYear"] > 1991) & (df["TripDurationinmin"] < 60)]
# young_long_bike = df.loc[(df["BirthYear"] > 1991) & (df["TripDurationinmin"] >= 60)]
# #adult
# adult_short_bike = df.loc[(df["BirthYear"] <= 1991) & (df["BirthYear"] >= 1961) & (df["TripDurationinmin"] < 60)]
# adult_long_bike = df.loc[(df["BirthYear"] <= 1991) & (df["BirthYear"] >= 1961) & (df["TripDurationinmin"] >= 60)]
# #elderly
# elderly_short_bike = df.loc[(df["BirthYear"] < 1961) & (df["TripDurationinmin"] < 60)]
# elderly_long_bike = df.loc[(df["BirthYear"] < 1961) & (df["TripDurationinmin"] >= 60)]

# print("number of young short bike: ", len(young_short_bike))
# print("number of younglong bike: ", len(young_long_bike))
# print("number of adult short bike: ", len(adult_short_bike))
# print("number of adult long bike: ", len(adult_long_bike))
# print("number of elderly short bike: ", len(elderly_short_bike))
# print("number of elderly long bike: ", len(elderly_long_bike))


#dictionary of start station and it's most common end station
# dicti = dict()
# start_station_set = set(df["StartStationName"])
# for name in start_station_set:
#     df_name = df.loc[df["StartStationName"] == name]
#     dicti[name] = df_name["EndStationName"].mode().iloc[0]

    # print(name, ", " ,dicti[name])


    #statistices between tart station and Trip Durationin min
    # print(name, " less then 60 minutes", len(df_name[df["TripDurationinmin"] < 60]))
    # print(name, " more then 60 minutes", len(df_name[df["TripDurationinmin"] >= 60]))


#user type and gender
# custumer_0 = df.loc[(df["UserType"] == "Customer") & (df["Gender"] == 0)]
# custumer_1 = df.loc[(df["UserType"] == "Customer") & (df["Gender"] == 1)]
# custumer_2 = df.loc[(df["UserType"] == "Customer") & (df["Gender"] == 2)]
# Subscriber_0 = df.loc[(df["UserType"] == "Subscriber") & (df["Gender"] == 0)]
# Subscriber_1 = df.loc[(df["UserType"] == "Subscriber") & (df["Gender"] == 1)]
# Subscriber_2 =  [(df["UserType"] == "Subscriber") & (df["Gender"] == 2)]

# print("number of custumer & 0: ", len(custumer_0))
# print("number of custumer & 1: ", len(custumer_1))
# print("number of custumer & 2: ", len(custumer_2))
# print("number of Subscriber & 0: ", len(Subscriber_0))
# print("number of Subscriber & 1: ", len(Subscriber_1))
# print("number of Subscriber & 2: ", len(Subscriber_2))

#all statistices parameters about TripDurationinmin
# print(df["TripDurationinmin"].describe())


#data discretization
# def binning(col, cut_points, labels=None):
#     minval = col.min()
#     maxvals= col.max()
#     break_points = [minval] + cut_points + [maxvals]
#     if not labels:
#         labels = range(len(cut_points)+1)
#     col_bin = pd.cut(col, bins=break_points, labels=labels, include_lowest=True)
#     return col_bin
#
# bins = [4, 6, 11]
# group_names = ['really short', 'short', 'medium', 'long']
# df_trip_time = df.loc[df["TripDurationinmin"] < 500]
# df_trip_time["TripDurationinmin"] = binning(df_trip_time["TripDurationinmin"], bins, group_names)
# print(df_trip_time)


#label incoder
# var_mod = ['StartStationName', 'EndStationName', 'UserType', 'TripDurationinmin']
# label_enc = LabelEncoder()
# for i in var_mod:
#     df_trip_time[i] = label_enc.fit_transform(df_trip_time[i])
#
# print(df_trip_time)


#splite and it to classes: night (00:00-05:59), morming (06:00-11:59), after_none (12:00-17:59) and late_evening (18:00-23:59)
start_time = df["StartTime"].to_list()
classes_lst = []
for ind in range(len(start_time)):
    str = start_time[ind].split(' ')
    time = str[1].split(':')
    #AM/PM
    if len(str) == 3:
        if str[2] == 'AM':
           if int(time[0]) >= 12:
               classes_lst.append('night')
           else:
               classes_lst.append('morning')
        elif str[2] == 'PM':
           if int(time[0]) >= 12:
               classes_lst.append('late_evening')
           else:
               classes_lst.append('after_none')
    #digital number between 00:00-23:59
    else:
        if int(time[0]) < 6:
           classes_lst.append('night')
        elif 6 <= int(time[0]) & int(time[0]) <= 11:
            classes_lst.append('morning')
        elif 12 <= int(time[0]) & int(time[0]) <= 17:
            classes_lst.append('after_none')
        else:
            classes_lst.append('late_evening')

# print("start time: \n", start_time)
print("list of classes classification: ", classes_lst)