"""
Script to download and process historic data.
Cleaned data and trained models put into flight_forecast/resources/generated
Prerequisite: Activate conda environment with:
    conda activate BTS_Flight_Forecast
"""
import sys
import pandas as pd
from utils import weather, data_processing, delay_predictor

RESOURCES_FOLDER_PATH = "resources"
AIRPORT_FOLDER_PATH = "resources/flight_data"
WEATHER_FOLDER_PATH = "resources/generated/weather_data"
PICKLE_FOLDER_PATH = "resources/generated/pickles"

if __name__ == '__main__':

    # Read the Airport Codes from CSV
    airports_data = pd.read_csv(RESOURCES_FOLDER_PATH + '/airport_codes.csv')

    # Fetch start and end years from input arguments
    try:
        start_year = int(sys.argv[1])
        end_year = int(sys.argv[2])
    except ValueError as error:
        raise ValueError("Expecting 'start year' and 'end year' as input. Integers required.")
    except IndexError as error:
        raise ValueError("Expecting 'start year' and 'end year' as input. Missing one or more arguments.")

    # Fetch and process historic weather data for the years in the input arguments.
    # cleaned data written to flight_forecast/resources/generated/weather_data
    weather.get_historic_weather_data(airports_data, start_year, end_year)

    # Process the historic flight data present in flight_forecast/resources/flight_data
    # merged data written to flight_forecast/resources/generated/pickles
    data_processing.create_dataset(airport_path=AIRPORT_FOLDER_PATH, weather_path=WEATHER_FOLDER_PATH)

    # Create regression and classification models trained on the combined data
    # Trained models stored as pickles in flight_forecast/resources/generated/pickles
    delay_predictor.create_model_from_dataset(data_path=PICKLE_FOLDER_PATH+"/combined_flight_data")