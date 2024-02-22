import pandas as pd
import requests
import time
import calendar

# token needs to be in config file
api_token = "e1f10a1e78da46f5b10a1e78da96f525"

# reading airport codes from csv
airport_codes = pd.read_csv('../resources/airport_codes.csv')

# TODO: use calendar module
months_days = pd.read_csv('../resources/month_days.csv', converters={'month' : str})

columns_of_interest = ['obs_id', # K+ airport code
                       'obs_name', # airport name
                       'valid_time_gmt', # start time
                       'expire_time_gmt',# end time
                       'day_ind', # night or day
                       'temp', # temperature
                       'dewPt', # dew point
                       'rh', # humidity
                       'wdir_cardinal', # wind direction
                       'gust', # wind gust
                       'wspd', # wind speed
                       'pressure', # pressure
                       'precip_hrly', # hourly precipitation in inch
                       'wx_phrase' # phrase
                       ]
def cleanData(airport_data_raw, location_code, columns_of_interest):

    airport_data_cleaned = airport_data_raw[columns_of_interest]
    airport_data_cleaned['location_id'] = location_code

    airport_data_cleaned['record_start_date'] = pd.to_datetime(airport_data_raw['valid_time_gmt'], unit='s')
    airport_data_cleaned['start_day'] = airport_data_cleaned['record_start_date'].dt.day
    airport_data_cleaned['start_month'] = airport_data_cleaned['record_start_date'].dt.month
    airport_data_cleaned['start_year'] = airport_data_cleaned['record_start_date'].dt.year
    airport_data_cleaned['start_isoweekday'] = airport_data_cleaned['record_start_date'].dt.dayofweek
    airport_data_cleaned['start_hour_gmt'] = airport_data_cleaned['record_start_date'].dt.hour
    airport_data_cleaned['start_minute_gmt'] = airport_data_cleaned['record_start_date'].dt.minute


    airport_data_cleaned['record_end_date'] =  pd.to_datetime(airport_data_raw['expire_time_gmt'], unit='s')
    airport_data_cleaned['end_hour_gmt'] = airport_data_cleaned['record_end_date'].dt.hour
    airport_data_cleaned['end_minute_gmt'] = airport_data_cleaned['record_end_date'].dt.minute

    airport_data_cleaned.drop(['record_start_date', 'record_end_date' ], axis=1)

    return airport_data_cleaned

def getWeatherDataAPI(startYear, endYear):

    for airport_index, ac in airport_codes.iterrows():

        url = 'https://api.weather.com/v1/location/K' +ac['Airport Code']+':9:US/observations/historical.json'

        obs = []

        for year in range(startYear, endYear):
            for index, md in months_days.iterrows():
                startDate = "{year}{month}{date}".format(year = year, month = md['month'], date = "01")
                endDate = "{year}{month}{date}".format(year = year, month = md['month'], date = md['end'])

                time.sleep(5)
                try:
                    params = dict(
                        apiKey=api_token,
                        units='e',
                        startDate=startDate,
                        endDate=endDate
                    )

                    resp = requests.get(url=url, params=params)
                    data = resp.json()
                    # print(data)
                    obs = obs + data['observations']
                    # print(ac['Airport Code'] + " : " + startDate + " to " + endDate + "csv length " + str(len(obs)))
                except Exception as e:
                    print("error while calling for airport code " + ac['Airport Code'] + " for dates " + startDate + ", " + endDate)
                    print(e)

        airport_data = pd.DataFrame(obs)
        airport_data_clean = cleanData( airport_data, ac['Airport Code'], columns_of_interest )
        airport_data_clean.to_csv("../resources/generated/" + ac['Airport Code'] + ".csv")
        break

if (__name__ == '__main__'):
    getWeatherDataAPI(2022, 2023)