"""
Script to download and process historic data.
Cleaned data and trained models put into BTS_Flight_Forecast/resources/generated
Prerequisite: Activate conda environment with:
    conda activate BTS_Flight_Forecast
"""
import pandas as pd
from utils import weather, data_processing, delay_predictor

RESOURCES_FOLDER_PATH = "resources"
AIRPORT_FOLDER_PATH = "resources/flight_data"
WEATHER_FOLDER_PATH = "resources/generated/weather_data"
PICKLE_FOLDER_PATH = "resources/generated/pickles"

if __name__ == '__main__':

    # Read the Airport Codes from CSV
    airports_data = pd.read_csv(RESOURCES_FOLDER_PATH + '/airport_codes.csv')

    # Default values for start and end years
    START_YEAR=2022
    END_YEAR=2023

    # Fetch and process historic weather data for the years in the input arguments.
    # cleaned data written to BTS_Flight_Forecast/resources/generated/weather_data
    weather.get_historic_weather_data(airports_data, START_YEAR, END_YEAR)

    # Process the historic flight data present in BTS_Flight_Forecast/resources/flight_data
    # merged data written to BTS_Flight_Forecast/resources/generated/pickles
    data_processing.create_dataset(airport_path=AIRPORT_FOLDER_PATH,
                                   weather_path=WEATHER_FOLDER_PATH)

    # Create regression and classification models trained on the combined data
    # Trained models stored as pickles in BTS_Flight_Forecast/resources/generated/pickles
    delay_predictor.create_model_from_dataset(data_path=PICKLE_FOLDER_PATH+"/combined_flight_data")
