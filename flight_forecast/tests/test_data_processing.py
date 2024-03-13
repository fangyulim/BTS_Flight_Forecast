'''
This module uses the unittest framework to run tests on data_processing.py.

[INSERT DOCUMENTATION]
'''

import unittest

from utils.data_processing import (
    combine_zipped_data,
    combine_weather_data,
    match_flight_and_weather_data,
    create_dataset
) # pylint: disable=import-error

AIRPORT_FOLDER_PATH = "./resources/flight_data"
WEATHER_FOLDER_PATH = "./resources/generated/weather_data"
PICKLE_FOLDER_PATH = "./resources/generated/pickles"
TEST_RESOURCES_PATH = "./resources/testing_resources"

class TestDataCombination(unittest.TestCase):
    '''
    This class contains and defines the unit tests run on data_processing.py
    '''

    # Running smoke tests

    def test_smoke_create_dataset(self):
        '''
        Runs a smoke test of combine_zipped_data, combine_weather_data,
        match_flight_and_weather_data, and create_dataset on a collection
        of typical airport and weather data.
        '''
        create_dataset(AIRPORT_FOLDER_PATH, WEATHER_FOLDER_PATH)
        self.assertTrue(True) # pylint: disable=redundant-unittest-assert

    # Running one-shot and pattern tests

    def test_one_shot_airport_combination(self):
        '''
        Tests that combine_zipped_data can correctly identify and combine two mock zipped csvs
        into the correct merged format.
        '''
        airport_df = combine_zipped_data(TEST_RESOURCES_PATH + "/test_airport_data")
        self.assertAlmostEqual(airport_df.shape[0], 18)
        self.assertAlmostEqual(airport_df.Month.unique().shape[0], 2)

    def test_one_shot_weather_combination(self):
        '''
        Tests that combine_zipped_data can correctly identify and combine two mock weather csvs
        into the correct merged format.
        '''
        weather_df = combine_weather_data(TEST_RESOURCES_PATH + "/test_weather_data")
        self.assertAlmostEqual(weather_df.shape[0], 22)
        self.assertAlmostEqual(weather_df.shape[1], 19)
        self.assertAlmostEqual(weather_df.airport_code.unique().shape[0], 2)

    # Running edge case tests

    def test_edge_case_empty_airport_folder(self):
        '''
        This module tests that a ValueError is raised when an empty folder is passed to
        the combine_zipped_data function.
        '''
        with self.assertRaises(ValueError):
            combine_zipped_data(TEST_RESOURCES_PATH + "/empty_test_folder")

    def test_edge_case_empty_weather_folder(self):
        '''
        This module tests that a ValueError is raised when an empty folder is passed to
        the combine_weather_data function.
        '''
        with self.assertRaises(ValueError):
            combine_weather_data(TEST_RESOURCES_PATH + "/empty_test_folder")

    def test_edge_case_airport_weather_time_mismatch(self):
        '''
        Tests that match_flight_and_weather_data throws an error if the given airport and weather
        datasets do not have a time overlap that can be used to match them together.
        '''
        with self.assertRaises(ValueError):
            test_airport_df = combine_zipped_data(TEST_RESOURCES_PATH + "/empty_test_folder")
            test_weather_df = combine_weather_data(TEST_RESOURCES_PATH + "/empty_test_folder")
            match_flight_and_weather_data(test_airport_df, test_weather_df)

    def test_edge_case_invalid_airport_names(self):
        '''
        Tests that combine_weather_data enforces 3-character airport codes for its file names.
        '''
        with self.assertRaises(ValueError):
            combine_weather_data(TEST_RESOURCES_PATH + "/invalid_name_weather_data")





if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataCombination)
    _ = unittest.TextTestRunner().run(suite)
