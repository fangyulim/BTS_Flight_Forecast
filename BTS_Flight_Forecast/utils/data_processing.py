"""
This script combines airport and weather data into one DataFrame.

This script loops through a folder of zipped airport data sourced from the Bureau of Transportation
Statistic's 'Marketing Carrier On-Time Reporting' database and assembles a DataFrame of flight
data. Then, the script loops through a folder of Meteostat airport weather csvs and assembles a
DataFrame of hourly airport weather data. These datasets are then matched to create a DataFrame
of flight data with weather columns corresponding to the local weather at the departure time of
each flight.
"""

import zipfile
import os
import sys
from datetime import datetime as dt
import pandas as pd

AIRPORT_FOLDER_PATH = "resources/flight_data"
WEATHER_FOLDER_PATH = "resources/generated/weather_data"
PICKLE_FOLDER_PATH = "resources/generated/pickles"


def combine_zipped_data(root_data_folder_path):
    '''
    This function opens all zip files in a given folder and combines any csv data found
    within them into a single Pandas DataFrame.
    
    Parameters
    ----------
    root_data_folder_path: A string containing the path to a folder containing zip files
                           with csv data.

    Returns
    -------
    A Pandas Dataframe with all csv data found in the given folder, combined together along
    the index (0) axis.
    '''
    # Creating empty list of DataFrames
    data_to_combine = []
    # Looping through raw data folder
    with os.scandir(root_data_folder_path) as root_data_folder:
        total_files = len(os.listdir(root_data_folder_path))
        current_progress = 0
        for entry in root_data_folder:
            # Displaying current progress
            current_progress += 1
            print(f"Processing airport file {current_progress}/{total_files} ...", end="\r")
            sys.stdout.flush()
            # Searching for zipped data
            if entry.name.endswith(".zip") and entry.is_file():
                # Opening zipped data folders
                with zipfile.ZipFile(root_data_folder_path + '/' + entry.name, "r") as zipped:
                    for name in zipped.namelist():
                        # Searching for csv files in zipped folders
                        if name.endswith('.csv'):
                            with zipped.open(name) as delay_data:
                                # Reading csv and adding to list of datasets
                                data_to_combine.append(pd.read_csv(delay_data, low_memory=False))
    # Attempting to combine and return collected data
    print('All files unpacked. Combining data...         ', end='\r')
    sys.stdout.flush()
    if len(data_to_combine) < 1:
        raise ValueError("The given folder path must contain a valid file. No zipped csvs found.")
    combined_data = pd.concat(data_to_combine)
    print('Airport data successfully combined!           ')
    sys.stdout.flush()
    return combined_data


def combine_weather_data(root_data_folder_path):
    '''
    This function finds all csvs of airport weather data in a given folder and combines them
    into a single Pandas DataFrame.

    Parameters
    ----------
    root_data_folder_path: String containing a path to a folder of airport weather data csvs.
                           Requires the csvs to be named after their respective airport codes.

    Returns
    -------
    A Pandas DataFrame containing the weather data from all airport weather csvs in the given
    folder, with an additional column containing the airport code for each measurement.
    '''

    data_to_combine = []
    with os.scandir(root_data_folder_path) as root_data_folder:
        total_files = len(os.listdir(root_data_folder_path))
        current_progress = 0
        for entry in root_data_folder:
            # Displaying current progress
            current_progress += 1
            print(f"Processing weather file {current_progress}/{total_files} ...", end="\r")
            sys.stdout.flush()
            # Searching for csv data
            if entry.is_file() and entry.name[-4:] == ".csv":
                # Collecting csv files for combination
                airport_df = pd.read_csv(entry.path)
                if len(entry.name) > 7:
                    raise ValueError("Weather data files must be named after 3-letter airport " +
                                      f"codes. Current name is {entry.name[:-4]}.")
                airport_df.loc[:, "airport_code"] = entry.name[:-4]
                airport_df = airport_df.fillna(value={"gust": 0})
                data_to_combine.append(airport_df)
    # Attempting to combine and return collected data
    print('All files unpacked. Combining data...         ', end='\r')
    sys.stdout.flush()
    if len(data_to_combine) < 1:
        raise ValueError("File path must contain a valid file. No files csvs found.")
    combined_data = pd.concat(data_to_combine)
    print('Weather data successfully combined!           ')
    sys.stdout.flush()
    return combined_data


def match_flight_and_weather_data(flight_df, weather_df):
    '''
    This function takes a Pandas DataFrame of flights and weather columns corresponding to
    the weather at departure time according to a DataFrame of airport weather conditions.

    Parameters
    ----------
    flight_df: A DataFrame of flights sourced from the Bureau of Transportation Statistics
    weather_df: A DataFrame of aiport weather sourced from Meteostat. Must contain airport codes.

    Returns
    -------
    A DataFrame containing the entries in flight_df with the weather data at each flight's
    departure time added as additional columns.
    '''
    if (not isinstance(flight_df, pd.DataFrame)) or (not isinstance(weather_df, pd.DataFrame)):
        raise TypeError("Both flight_df and weather_df must be Pandas DataFrames. Currently, " + \
                        f"they are a {type(flight_df)} and a {type(weather_df)} respectively.")
    # Preparing flight dataframe to recieve weather data rows
    flight_df = flight_df.reset_index()
    flight_df.loc[:, weather_df.columns] = pd.NA
    weather_cols = weather_df.columns
    # Testing if any matching data exists
    # Recording airport counts to display function's current progress
    num_airports_to_inspect = len(flight_df.Origin.unique())
    airports_with_known_weather_data = weather_df.airport_code.unique()
    for ind, airport_code in enumerate(list(flight_df.Origin.unique())):
        if airport_code in airports_with_known_weather_data:
            print(f"Currently processing airport code {airport_code}." + \
                  f"{ind}/{num_airports_to_inspect}  ", end='\r')
            sys.stdout.flush()
            # Obtaining flight data for current airport and sorting by departure time
            airport_flight_df = flight_df[flight_df.Origin == airport_code]
            airport_flight_df.loc[:, "FlightDate"] = (airport_flight_df.FlightDate + " " +
                                                      airport_flight_df.DepTime \
                                                      .apply(int) \
                                                      .apply(str) \
                                                      .str.zfill(4) \
                                                      .apply(lambda time: time \
                                                          if time != "2400" \
                                                          else "2359"))
            # parse_airport_date = lambda date: dt.strptime(date, "%Y-%m-%d %H%M")
            time_str = ("%Y-%m-%d %H%M",)
            airport_flight_df.loc[:, "FlightDate"] = airport_flight_df.FlightDate \
                .apply(dt.strptime, \
                       args=time_str)
            airport_flight_df = airport_flight_df.sort_values(by="FlightDate")
            # Obtaining weather data for current airport and sorting by measurement time
            airport_weather_df = weather_df[weather_df.airport_code == airport_code]
            # parse_weather_date = lambda date: dt.strptime(date, "%Y-%m-%d %H:%M:%S")
            time_str = ("%Y-%m-%d %H:%M:%S",)
            airport_weather_df.loc[:, "record_start_date"] = airport_weather_df.record_start_date \
                .apply(dt.strptime, \
                       args=time_str)
            airport_weather_df = airport_weather_df.sort_values(by="record_start_date")
            # Checking that weather data aligns with airport dates
            if airport_weather_df.record_start_date.min() > airport_flight_df.FlightDate.max() or \
               airport_weather_df.record_start_date.max() < airport_flight_df.FlightDate.min():
                raise ValueError("The flight dataset and weather dataset must have" + \
                                 " overlapping time periods for each airport of interest." + \
                                 "For the current airport, the flight dataset covers" + \
                                 f"{airport_weather_df.record_start_date.min()} to " + \
                                 f"{airport_weather_df.record_start_date.max()} " + \
                                 "While the weather dataset covers " + \
                                 f"{airport_flight_df.FlightDate.min()} to " + \
                                 f"{airport_flight_df.FlightDate.max()}.")
            # Matching flight and weather data by ascending along both date columns
            current_flight = 0
            current_weather = 0
            while current_flight < airport_flight_df.shape[0]:
                while airport_flight_df.FlightDate.iloc[current_flight] > \
                        airport_weather_df.record_start_date.iloc[current_weather]:
                    current_weather += 1
                flight_ind = airport_flight_df.index[current_flight]
                flight_df.loc[flight_ind, weather_cols]=airport_weather_df.iloc[current_weather, :]
                current_flight += 1
    print("Data successfully attached!                                       ", end="\r")
    sys.stdout.flush()
    return flight_df


def create_dataset(airport_path=AIRPORT_FOLDER_PATH, weather_path=WEATHER_FOLDER_PATH,
                   pickle_path=PICKLE_FOLDER_PATH):
    '''
    Creates a combined airport/weather dataset from paths to individual data files.

    Parameters
    ----------
    airport_path: A string containing the path to a folder containing zip files with csv data
                  sourced from the Bureau of Transportation Statistics.
    weather_path: String containing a path to a folder of Meteostat airport weather data csvs.
                  Requires the csvs to be named after their respective airport codes.
    '''
    # Preparing flight data
    flight_data = combine_zipped_data(airport_path)
    flight_data = flight_data.dropna(subset=["FlightDate", "DepTime"])
    # Removing all columns that are more than 5% NaN values
    flight_data = flight_data[flight_data.columns[flight_data.isna().sum() < \
                                                  flight_data.shape[0] / 20]]
    # Dropping rows of data with NaN in the target delay column (ArrDel15)
    flight_data = flight_data.dropna(subset="ArrDel15")

    # Adding weather data
    weather_data = combine_weather_data(weather_path)
    # Dropping extremely small number of rows with null windspeed/dewpoint/temp values
    weather_data = weather_data.dropna()

    # Restricting attachment to only airports with known weather data
    relevant_flights_df = flight_data[flight_data.Origin.isin(weather_data.airport_code.unique())]
    combined_flight_data = match_flight_and_weather_data(relevant_flights_df, weather_data)

    combined_flight_data.to_pickle(pickle_path + "/combined_flight_data")
