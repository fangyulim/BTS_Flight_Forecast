"""
Provides functions for gathering weather data, including historical and forecast information,
for specified airports.

Functions:
- get_month_range(year, month):
    Calculates start and end dates for a month.
- generate_date_ranges(years):
    Generates a list of dictionaries containing date ranges for a year range.
- enrich_date_time(weather_df):
    Adds derived date and time information to a weather DataFrame.
- clean_historic_weather_data(weather_data_raw, location_code, columns_of_interest):
    Cleans and enriches historical weather data.
- get_historic_weather_data(airports, start_year, end_year):
    Retrieves and saves historical weather data for multiple airports.
- refine_forecasted_data(forecasted_weather_df_raw):
    Refines and reformats forecasted weather data.
- get_weather_forecast(airport_code):
    Fetches and refines 15-day weather forecast for an airport.

This module requires the following external libraries:
- pandas
- datetime
- calendar
- requests
"""
import time
import calendar

from datetime import date, timedelta

import requests

import pandas as pd

# The API token required for accessing the weather API.
API_TOKEN = "e1f10a1e78da46f5b10a1e78da96f525"

WEATHER_FORECAST_URL = 'https://api.weather.com/v3/wx/forecast/hourly/15day'

"""
COI_HISTORIC: A list of strings specifying the columns to extract
from historical weather data.
"""
COI_HISTORIC = [
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

"""
COI_FORECASTED: A list of strings specifying the columns to extract
from forecasted weather data.
"""

COI_FORECASTED = [
    'validTimeUtc',
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
    'wxPhraseShort'
]


def get_month_range(year, month):
    """
    This function returns a tuple containing the start and end dates of
    a specific month in a given year.

    Args:
        year (int): The year for which the date range is desired.
        month (int): The month number (1-12) for which the date range is desired.

    Returns:
        tuple: A tuple containing the start and end dates of a month.
    """
    # Create the first day of the month
    start_date = date(year, month, 1)
    # For February, check if it's a leap year to get the correct end date
    if month == 2:
        end_date = start_date + timedelta(days=27 + calendar.isleap(year))
    else:
        # For other months, use the appropriate number of days based on month length
        end_date = start_date + timedelta(days=(30 if month in (1, 3, 5, 7, 8, 10, 12) else 29))
    return start_date, end_date


def generate_date_ranges(years):
    """
    This function generates a list of dictionaries containing start and end dates
    for each month in a given list of years.

    Args:
        years (list): A list of integers representing the years for which date ranges are desired.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'year', 'month', 'start_date',
         and 'end_date' keys.
    """
    date_ranges = []
    for year in years:
        for month in range(1, 13):
            start_date, end_date = get_month_range(year, month)
            date_ranges.append({
                'year': year,
                'month': month,
                'start_date': start_date.strftime('%Y%m%d'),
                'end_date': end_date.strftime('%Y%m%d')
            })
    return date_ranges


def enrich_date_time(weather_df):
    """
    Enriches weather data with derived date/time columns and drops originals.

    Args:
        weather_df (pd.DataFrame): DataFrame containing weather data.

    Returns:
        pd.DataFrame: DataFrame with enriched date/time information.

    Raises:
        ValueError: If 'valid_time_gmt' or 'expire_time_gmt' is missing.

    Assumes 'valid_time_gmt' and 'expire_time_gmt' are in UTC timestamps.
    """

    if 'valid_time_gmt' not in weather_df.columns:
        raise ValueError("Missing 'valid_time_gmt' in weather data")
    if 'expire_time_gmt' not in weather_df.columns:
        raise ValueError("Missing 'expire_time_gmt' in weather data")

    weather_df['record_start_date'] = pd.to_datetime(weather_df['valid_time_gmt'], unit='s')
    weather_df['start_day'] = weather_df['record_start_date'].dt.day
    weather_df['start_month'] = weather_df['record_start_date'].dt.month
    weather_df['start_year'] = weather_df['record_start_date'].dt.year
    weather_df['start_isoweekday'] = weather_df['record_start_date'].dt.dayofweek
    weather_df['start_hour_gmt'] = weather_df['record_start_date'].dt.hour
    weather_df['start_minute_gmt'] = weather_df['record_start_date'].dt.minute

    weather_df['record_end_date'] = pd.to_datetime(weather_df['expire_time_gmt'], unit='s')
    weather_df['end_hour_gmt'] = weather_df['record_end_date'].dt.hour
    weather_df['end_minute_gmt'] = weather_df['record_end_date'].dt.minute

    weather_df.drop(['record_start_date', 'record_end_date'], axis=1)

    return weather_df


def clean_historic_weather_data(weather_data_raw, location_code, columns_of_interest):
    """
    Cleans and enriches historical weather data: selects relevant columns, adds location ID,
     and enriches date/time.

    Args:
        weather_data_raw (pd.DataFrame): Raw weather data.
        location_code (str): Airport code for the data's location.
        columns_of_interest (list): Columns to keep from the raw data.

    Returns:
        pd.DataFrame: Cleaned and enriched weather data.
    """

    weather_data_cleaned = weather_data_raw[columns_of_interest]
    weather_data_cleaned['location_id'] = location_code

    return enrich_date_time(weather_data_cleaned)


def get_historic_weather_data(airports, start_year, end_year):
    """
     Fetches and saves historical weather data for airports over a specified period.

     Args:
         airports (pd.DataFrame): DataFrame containing airport information.
         start_year (int): Starting year (inclusive).
         end_year (int): Ending year (inclusive).

     Raises:
         ValueError: If start_year > end_year.

     Iterates through airports, fetching data for each within the year range,
     saving cleaned/enriched data as CSV files.
     """

    if start_year > end_year:
        raise ValueError("Start year should be less than or equal to end year")

    months_days = generate_date_ranges(list(range(start_year, end_year + 1)))
    print(months_days)

    for airport in airports['Airport Code']:
        historic_weather_api = f"https://api.weather.com/v1/location/K{airport}:9:US/observations/historical.json"

        obs = []

        for time_period in months_days:
            time.sleep(5)
            try:
                params = {
                    'apiKey': API_TOKEN,
                    'units': 'e',
                    'startDate': time_period['start_date'],
                    'endDate': time_period['end_date']
                }

                resp = requests.get(url=historic_weather_api, params=params, timeout=15)
                data = resp.json()

                # raise exception if observations is not present in the data
                obs = obs + data['observations']

            except Exception as e:
                print(f"Error while fetching weather data for {airport}")
                print(e)
                # should we raise an exception here? or just notify the user?

        airport_data = pd.DataFrame(obs)
        airport_data_clean = clean_historic_weather_data(airport_data, airport, COI_HISTORIC)
        airport_data_clean.to_csv("../../../resources/generated/" + airport + ".csv")
        break


def refine_forecasted_data(forecasted_weather_df_raw):
    """
    Refines forecasted weather data: selects columns, renames, and enriches date/time.

    Args:
        forecasted_weather_df_raw (pd.DataFrame): Raw forecasted weather data.

    Returns:
        pd.DataFrame: Refined forecasted weather data.
    """
    forecasted_weather_data = forecasted_weather_df_raw[COI_FORECASTED]

    # rename columns
    column_mapping = {'validTimeUtc': 'valid_time_gmt',
                      'expirationTimeUtc': 'expire_time_gmt',
                      'dayOrNight': 'day_ind',
                      'temperature': 'temp',
                      'temperatureDewPoint': 'dewPt',
                      'relativeHumidity': 'rh',
                      'windDirectionCardinal': 'wdir_cardinal',
                      'windGust': 'gust',
                      'windSpeed': 'wspd',
                      'pressureMeanSeaLevel': 'pressure',
                      'wxPhraseShort': 'wx_phrase'}

    forecasted_weather_data = forecasted_weather_data.rename(
        columns=column_mapping)

    # refine start and end times for each record
    return enrich_date_time(forecasted_weather_data)


def get_weather_forecast(airport_code, timestamp):
    """Fetches weather forecast data for a given airport code and timestamp.

    Args:
    airport_code (str): The 3-letter ICAO code of the airport.
    timestamp (int): The Unix timestamp representing the desired forecast time.

    Returns:
    pd.DataFrame: The refined weather forecast DataFrame, containing data for the specified timestamp.

    Raises:
    Exception: If any errors occur during API calls or data processing.
    """

    try:
        params = {
            'apiKey': API_TOKEN,
            'icaoCode': f'K{airport_code}',
            'units': 'm',
            'format': 'json',
            'language': 'en-US'
        }

        resp = requests.get(url=WEATHER_FORECAST_URL, params=params, timeout=15)
        print(resp.request.url)
        response_data = resp.json()

        # transpose data from array to dictionary list
        forecasted_weather_df = pd.DataFrame(response_data)
        forecasted_weather_df["expirationTimeUtc"] = (forecasted_weather_df["validTimeUtc"].shift(-1)
                                                      .fillna(forecasted_weather_df["validTimeUtc"] + 3600))

        refined_weather_df = refine_forecasted_data(forecasted_weather_df)

        focused_forecast_df = refined_weather_df[
            (refined_weather_df['valid_time_gmt'] <= timestamp) & (timestamp < refined_weather_df['expire_time_gmt'])]

        return focused_forecast_df

    except Exception as e:
        print(e)


if __name__ == '__main__':
    # Read the Airport Codes from CSV
    # airports_data = pd.read_csv('../../../resources/airport_codes.csv')

    # get_historic_weather_data(airports_data, 2022, 2023)

    print(get_weather_forecast('SEA', 1709770534))
