import time
import requests

import pandas as pd

# token needs to be in config file
API_TOKEN = "e1f10a1e78da46f5b10a1e78da96f525"

# reading airport codes from csv
airport_codes = pd.read_csv('../../../resources/airport_codes.csv')

# TODO: use calendar module
months_days = pd.read_csv('../../../resources/month_days.csv', converters={'month': str})

historic_columns_of_interest = [
    'obs_id',  # K+ airport code
    'obs_name',  # airport name
    'valid_time_gmt',  # start time
    'expire_time_gmt',  # end time
    'day_ind',  # night or day
    'temp',  # temperature
    'dewPt',  # dew point
    'rh',  # humidity
    'wdir_cardinal',  # wind direction
    'gust',  # wind gust
    'wspd',  # wind speed
    'pressure',  # pressure
    'precip_hrly',  # hourly precipitation in inch
    'wx_phrase'  # phrase
]

forecasted_columns_of_interest = ['validTimeUtc',
                                  'expirationTimeUtc',
                                  'dayOrNight',
                                  'temperature',
                                  'temperatureDewPoint',
                                  'relativeHumidity',
                                  'windDirectionCardinal',
                                  'windGust',
                                  'windSpeed',
                                  'pressureMeanSeaLevel',
                                  # precipitation
                                  'wxPhraseShort']


def enrich_date_time(df):
    df['record_start_date'] = pd.to_datetime(df['valid_time_gmt'], unit='s')
    df['start_day'] = df['record_start_date'].dt.day
    df['start_month'] = df['record_start_date'].dt.month
    df['start_year'] = df['record_start_date'].dt.year
    df['start_isoweekday'] = df['record_start_date'].dt.dayofweek
    df['start_hour_gmt'] = df['record_start_date'].dt.hour
    df['start_minute_gmt'] = df['record_start_date'].dt.minute

    df['record_end_date'] = pd.to_datetime(df['expire_time_gmt'], unit='s')
    df['end_hour_gmt'] = df['record_end_date'].dt.hour
    df['end_minute_gmt'] = df['record_end_date'].dt.minute

    df.drop(['record_start_date', 'record_end_date'], axis=1)

    return df


def clean_historic_weather_data(weather_data_raw, location_code, columns_of_interest):
    weather_data_cleaned = weather_data_raw[columns_of_interest]
    weather_data_cleaned['location_id'] = location_code

    return enrich_date_time(weather_data_cleaned)


def get_historic_weather_data(start_year, end_year):
    if start_year > end_year:
        raise ValueError("Start year should be less than or equal to end year")

    for airport_index, ac in airport_codes.iterrows():

        url = f"https://api.weather.com/v1/location/K{ac['Airport Code']}:9:US/observations/historical.json"

        obs = []

        for year in range(start_year, end_year + 1):
            for index, md in months_days.iterrows():
                start_date = "{year}{month}{date}".format(year=year, month=md['month'], date="01")
                end_date = "{year}{month}{date}".format(year=year, month=md['month'], date=md['end'])

                time.sleep(5)
                try:
                    params = dict(
                        apiKey=API_TOKEN,
                        units='e',
                        startDate=start_date,
                        endDate=end_date
                    )

                    resp = requests.get(url=url, params=params)
                    data = resp.json()

                    # raise exception if observations is not present in the data
                    obs = obs + data['observations']

                except Exception as e:
                    print("error while calling for airport code " + ac['Airport Code'] + " for dates " + start_date + ", " + end_date)
                    print(e)
                    # should we raise an exception here? or just notify the user?

        airport_data = pd.DataFrame(obs)
        airport_data_clean = clean_historic_weather_data(airport_data, ac['Airport Code'], historic_columns_of_interest)
        airport_data_clean.to_csv("../resources/generated/" + ac['Airport Code'] + ".csv")
        break


def refine_forecasted_data(forecasted_weather_df_raw):
    forecasted_weather_data = forecasted_weather_df_raw[forecasted_columns_of_interest]

    # rename columns
    forecasted_weather_data = forecasted_weather_data.rename(columns={'validTimeUtc': 'valid_time_gmt',
                                                                      'expirationTimeUtc': 'expire_time_gmt',
                                                                      'dayOrNight': 'day_ind',
                                                                      'temperature': 'temp',
                                                                      'temperatureDewPoint': 'dewPt',
                                                                      'relativeHumidity': 'rh',
                                                                      'windDirectionCardinal': 'wdir_cardinal',
                                                                      'windGust': 'gust',
                                                                      'windSpeed': 'wspd',
                                                                      'pressureMeanSeaLevel': 'pressure',
                                                                      'wxPhraseShort': 'wx_phrase'})

    # refine start and end times for each record
    return enrich_date_time(forecasted_weather_data)


def get_weather_forecast(airport_code):
    url = 'https://api.weather.com/v3/wx/forecast/hourly/15day'

    try:
        params = dict(
            apiKey=API_TOKEN,
            icaoCode='K' + airport_code,
            units='m',
            format='json',
            language='en-US'
        )

        resp = requests.get(url=url, params=params)
        response_data = resp.json()

        # transpose data from array to dictionary list
        forecasted_weather_df = pd.DataFrame(response_data)

        return refine_forecasted_data(forecasted_weather_df)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    get_historic_weather_data(2022, 2023)
