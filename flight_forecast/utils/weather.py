"""
Provides functions for gathering weather data, including historical and forecast information,
for specified airports.

Functions:
- _get_month_range(year, month):
    Calculates start and end dates for a month.
- _generate_date_ranges(years):
    Generates a list of dictionaries containing date ranges for a year range.
- _enrich_date_time(weather_df):
    Adds derived date and time information to a weather DataFrame.
- _clean_historic_weather_data(weather_data_raw, location_code, columns_of_interest):
    Cleans and enriches historical weather data.
- get_historic_weather_data(airports, start_year, end_year):
    Retrieves and saves historical weather data for multiple airports.
- _refine_forecasted_data(forecasted_weather_df_raw):
    Refines and reformats forecasted weather data.
- get_weather_forecast(airport_code, timestamp):
    Fetches and refines 15-day weather forecast for an airport.

This module requires the following external libraries:
- pandas
- datetime
- calendar
- requests
"""
import time
import calendar
import sys

from datetime import date, timedelta

import numpy
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

"""
COI_WEATHER_FORECAST: A list of strings specifying the data to extract from 
filtered and refined weather data.
"""
COI_WEATHER_FORECAST = [
    'day_ind',  # night or day
    'temp',  # temperature
    'dewPt',  # dew point
    'rh',  # humidity
    'wdir_cardinal',  # wind direction
    'gust',  # wind gust
    'wspd',  # wind speed
    'pressure',  # pressure
    'wx_phrase'  # phrase
]

WEATHER_FORECAST_COLUMN_MAP = {'validTimeUtc': 'valid_time_gmt',
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


def _get_month_range(year, month):
    """
    This function returns a tuple containing the start and end dates of
    a specific month in a given year.

    Args:
        year (int): The year for which the date range is desired.
        month (int): The month number (1-12) for which the date range is desired.

    Returns:
        tuple: A tuple containing the start and end dates of a month.

    Raises:
        ValueError: If 'month' or 'year' is invalid.
        TypeError: If 'month' or 'year' is not integer.
    """

    try:
        # Create the first day of the month
        start_date = date(year, month, 1)
        # For February, check if it's a leap year to get the correct end date
        if month == 2:
            end_date = start_date + timedelta(days=27 + calendar.isleap(year))
        else:
            # For other months, use the appropriate number of days based on month length
            end_date = start_date + timedelta(days=(30 if month in (1, 3, 5, 7, 8, 10, 12) else 29))
        return start_date, end_date
    except TypeError as type_error:
        raise type_error
    except ValueError as value_error:
        raise value_error


def _generate_date_ranges(years):
    """
    This function generates a list of dictionaries containing start and end dates
    for each month in a given list of years.

    Args:
        years (range): A range of years for which date ranges are desired.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'year', 'month', 'start_date',
         and 'end_date' keys.

    Raises:
        TypeError: If 'years' is not a range.
        ValueError: If 'years' is not a valid range
    """

    if not isinstance(years, range):
        raise TypeError("'years' is not a range")
    if years.start <= 0 or years.stop <= 0:
        raise ValueError("'years' is not a valid range")

    date_ranges = []
    for year in years:
        for month in range(1, 13):
            start_date, end_date = _get_month_range(year, month)
            date_ranges.append({
                'year': year,
                'month': month,
                'start_date': start_date.strftime('%Y%m%d'),
                'end_date': end_date.strftime('%Y%m%d')
            })
    return date_ranges


def _enrich_date_time(weather_df):
    """
    Enriches weather data with derived date/time columns and drops originals.

    Args:
        weather_df (pd.DataFrame): DataFrame containing weather data.

    Returns:
        pd.DataFrame: DataFrame with enriched date/time information.

    Raises:
        ValueError: If 'valid_time_gmt' or 'expire_time_gmt' is missing.
        TypeError: If 'valid_time_gmt' or 'expire_time_gmt' is invalid.

    Assumes 'valid_time_gmt' and 'expire_time_gmt' are in UTC timestamps (in seconds).
    """

    if 'valid_time_gmt' not in weather_df.columns:
        raise ValueError("Missing 'valid_time_gmt' in weather data")
    if weather_df.dtypes['valid_time_gmt'] not in [int, numpy.int32, numpy.int64]:
        raise TypeError("Invalid 'valid_time_gmt' in weather data")

    if 'expire_time_gmt' not in weather_df.columns:
        raise ValueError("Missing 'expire_time_gmt' in weather data")
    if weather_df.dtypes['expire_time_gmt'] not in [int, numpy.int32, numpy.int64]:
        raise TypeError("Invalid 'expire_time_gmt' in weather data")

    weather_df.loc[:, 'record_start_date'] = pd.to_datetime(weather_df['valid_time_gmt'], unit='s')
    weather_df.loc[:, 'record_end_date'] = pd.to_datetime(weather_df['expire_time_gmt'], unit='s')

    return weather_df


def _clean_historic_weather_data(weather_data_raw, location_code, columns_of_interest):
    """
    Cleans and enriches historical weather data: selects relevant columns, adds location ID,
     and enriches date/time.

    Args:
        weather_data_raw (pd.DataFrame): Raw weather data.
        location_code (str): Airport code for the data's location.
        columns_of_interest (list): Columns to keep from the raw data.

    Returns:
        pd.DataFrame: Cleaned and enriched weather data.

    Raises:
        ValueError: If 'weather_data_raw' does not have all 'columns_of_interest'
    """

    if not set(columns_of_interest) <= set(weather_data_raw.columns):
        raise ValueError("'weather_data_raw' does not have all the 'columns_of_interest'")

    weather_data_cleaned = weather_data_raw[columns_of_interest].copy()
    weather_data_cleaned.loc[:, 'location_id'] = location_code

    return _enrich_date_time(weather_data_cleaned)


def get_historic_weather_data(airports, start_year, end_year):
    """
     Fetches and saves historical weather data for airports over a specified period.

     Args:
         airports (pd.DataFrame): DataFrame containing airport information.
         start_year (int): Starting year (inclusive).
         end_year (int): Ending year (inclusive).

     Raises:
         TypeError: If start_year or end_year is not an integer
                    If 'airports' is not a dataframe
         ValueError: If start_year <= 0 or end_year <= 0 or start_year > end_year
                     If 'Airport Code' not present in the 'airports' dataframe


     Iterates through airports, fetching data for each within the year range,
     saving cleaned/enriched data as CSV files.
     """
    # check validity of start_year and end_year
    if not isinstance(start_year, int) or not isinstance(end_year, int):
        raise TypeError(" 'start_year' or 'end_year' is not an integer")
    if start_year <= 0 or end_year <= 0:
        raise ValueError("Invalid 'start_year' or 'end_year' in the input")
    if start_year > end_year:
        raise ValueError("'start_year' should be less than or equal to 'end_year'")

    # check validity of 'airports'
    if not isinstance(airports, pd.DataFrame):
        raise TypeError("'airports' is not a valid dataframe")
    if 'Airport Code' not in airports.columns:
        raise ValueError("'Airport Code' not present in the input dataframe")

    months_days = _generate_date_ranges(range(start_year, end_year + 1))

    for ind, airport in enumerate(airports['Airport Code']):
        progress_str = f"Getting weather for airport {airport}. " + \
                       f"({ind}/{airports['Airport Code'].shape[0]})"
        print(progress_str, end="\r")
        sys.stdout.flush()
        historic_weather_api = f"https://api.weather.com/v1/location/K{airport}" + \
                               ":9:US/observations/historical.json"

        obs = []

        for time_period in months_days:
            time.sleep(1)
            params = {
                'apiKey': API_TOKEN,
                'units': 'e',
                'startDate': time_period['start_date'],
                'endDate': time_period['end_date']
            }

            resp = requests.get(url=historic_weather_api, params=params, timeout=15)

            if 200 <= resp.status_code < 300:

                data = resp.json()

                if 'observations' in data.keys():
                    obs = obs + data['observations']
                else:
                    print(f"Error while fetching historic weather data for {airport} between the "
                          f"dates {time_period['start_date']}, {time_period['end_date']}."
                          f"Response does not have 'observations'.")
            else:
                print(f"Error while fetching historic weather data for {airport} "
                      f"between the dates {time_period['start_date']}, {time_period['end_date']}."
                      "Response code indicates failure.")

        if len(obs) > 0:
            airport_data = pd.DataFrame(obs)
            airport_data_clean = _clean_historic_weather_data(airport_data, airport, COI_HISTORIC)
            airport_data_clean.to_csv("resources/generated/weather_data/" + airport + ".csv")


def _refine_forecasted_data(forecasted_weather_df_raw, columns_of_interest):
    """
    Refines forecasted weather data: selects columns, renames, and enriches date/time.

    Args:
        forecasted_weather_df_raw (pd.DataFrame): Raw forecasted weather data.
        columns_of_interest (list): Columns to keep from the raw forecast data.

    Returns:
        pd.DataFrame: Refined forecasted weather data.
    """

    if not set(columns_of_interest) <= set(forecasted_weather_df_raw.columns):
        raise ValueError("'forecasted_weather_df_raw' does not have all the columns of interest")

    forecasted_weather_data = forecasted_weather_df_raw[columns_of_interest]

    forecasted_weather_data = forecasted_weather_data.rename(
        columns=WEATHER_FORECAST_COLUMN_MAP)

    # refine start and end times for each record
    return _enrich_date_time(forecasted_weather_data)


def get_weather_forecast(airport_code, timestamp):
    """Fetches weather forecast data for a given airport code and timestamp.

    Args:
        airport_code (str): The 3-letter ICAO code of the airport.
        timestamp (int): The Unix timestamp representing the desired forecast time.

    Returns:
        pd.DataFrame: The refined weather forecast DataFrame, containing data for the
         specified timestamp.

    Raises:
        TypeError: 'airport_code' or 'timestamp' are of incorrect type.
        requests.HttpError: If the forecast API returns a 4xx or 5xx response code.
        ValueError: If any errors occur during API calls or data processing.
    """

    if not isinstance(airport_code, str):
        raise TypeError("Invalid 'airport_code'.")

    if type(timestamp) not in [int, numpy.int32, numpy.int64]:
        raise TypeError("Invalid 'timestamp'.")

    params = {
        'apiKey': API_TOKEN,
        'icaoCode': f'K{airport_code}',
        'units': 'm',
        'format': 'json',
        'language': 'en-US'
    }

    resp = requests.get(url=WEATHER_FORECAST_URL, params=params, timeout=15)

    # raise an error for 4xx and 5xx response codes
    resp.raise_for_status()
    response_data = resp.json()

    # transpose data from array to dictionary list
    forecasted_weather_df = pd.DataFrame(response_data)
    if 'validTimeUtc' not in forecasted_weather_df.columns:
        raise ValueError(f"Missing 'validTimeUtc' in the forecasted weather data for "
                         f"airport {airport_code}")

    forecasted_weather_df.loc[:, "expirationTimeUtc"] = \
        (forecasted_weather_df["validTimeUtc"]
         .shift(-1)
         .fillna(forecasted_weather_df["validTimeUtc"]
                 + 3600))

    refined_weather_df = _refine_forecasted_data(forecasted_weather_df, COI_FORECASTED)

    focused_forecast_df = refined_weather_df[
        (refined_weather_df['valid_time_gmt'] <= timestamp) & \
        (timestamp < refined_weather_df['expire_time_gmt'])]
    focused_forecast_df = focused_forecast_df[COI_WEATHER_FORECAST]

    if len(focused_forecast_df) == 0:
        raise ValueError(f"Forcast data unavailable for given airport {airport_code} at "
                         f"time {timestamp}")
    return focused_forecast_df


if __name__ == '__main__':
    # Read the Airport Codes from CSV
    airports_data = pd.read_csv('resources/airport_codes.csv')
    get_historic_weather_data(airports_data, 2022, 2023)
