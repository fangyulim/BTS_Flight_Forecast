"""
This module contains unit tests for various function defined in the `weather` module.
"""

import unittest
from datetime import date
from unittest import mock

import pandas as pd
import requests

from utils.weather import (
    _get_month_range,
    _generate_date_ranges,
    _enrich_date_time,
    _clean_historic_weather_data,
    _refine_forecasted_data,
    get_historic_weather_data,
    get_weather_forecast
)

sample_weather_data_historic = {
    "valid_time_gmt": 1709931638,  # 8th March 2024
    "expire_time_gmt": 1710018038,
    "day_ind": "N",
    "temp": 20,
    "dewPt": 15,
    "rh": 75,
    "wdir_cardinal": "N",
    "gust": 10,
    "wspd": 5,
    "pressure": 1013,
    "precip_hrly": 0,
    "wx_phrase": "Clear",
}

sample_weather_data_forecasted = {
    'validTimeUtc': 1709931638,  # 8th March 2024
    'expirationTimeUtc': 1710018038,
    'dayOrNight': 'N',
    'temperature': 20,
    'temperatureDewPoint': 15,
    'relativeHumidity': 75,
    'windDirectionCardinal': 'N',
    'windGust': 10,
    'windSpeed': 5,
    'pressureMeanSeaLevel': 1013,
    'wxPhraseShort': 'Clear'
}


class TestWeather(unittest.TestCase):

    def test_get_month_range_oneshot(self):
        """
        Tests that `_get_month_range` returns the correct start and end dates for a month.
        """

        start_date, end_date = _get_month_range(2023, 1)
        self.assertEqual(start_date, date(2023, 1, 1))
        self.assertEqual(end_date, date(2023, 1, 31))

        start_date, end_date = _get_month_range(2024, 2)
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

    def test_get_month_range_edge(self):
        """
        Tests that `_get_month_range` raises error for invalid inputs.
        """

        # Value Errors:
        with self.assertRaises(ValueError):
            _get_month_range(2023, -1)
        with self.assertRaises(ValueError):
            _get_month_range(2023, 13)
        with self.assertRaises(ValueError):
            _get_month_range(-2023, 1)

        # Type Errors:
        with self.assertRaises(TypeError):
            _get_month_range(2023, '-1')
        with self.assertRaises(TypeError):
            _get_month_range('2023', 13)

    def test_generate_date_ranges_oneshot(self):
        """
        Tests that `_generate_date_ranges` returns correct list of start and end dates per month.
        """
        date_ranges = _generate_date_ranges(range(2023, 2025))
        expected_ranges_start = [
            {"year": 2023, "month": 1, "start_date": "20230101", "end_date": "20230131"},
            {"year": 2023, "month": 2, "start_date": "20230201", "end_date": "20230228"},
            {"year": 2023, "month": 3, "start_date": "20230301", "end_date": "20230331"}
        ]

        expected_ranges_end = [
            {"year": 2024, "month": 10, "start_date": "20241001", "end_date": "20241031"},
            {"year": 2024, "month": 11, "start_date": "20241101", "end_date": "20241130"},
            {"year": 2024, "month": 12, "start_date": "20241201", "end_date": "20241231"}
        ]
        self.assertEqual(date_ranges[:3], expected_ranges_start)  # Check first 3 elements
        self.assertEqual(date_ranges[-3:], expected_ranges_end)  # Check last 3 elements

    def test_generate_date_ranges_edge(self):
        """
        Tests that `_generate_date_ranges` raises error for invalid inputs.
        """

        with self.assertRaises(ValueError):
            _generate_date_ranges(range(-2023, 2025))
        with self.assertRaises(TypeError):
            _generate_date_ranges([2023, 2024])
        with self.assertRaises(TypeError):
            _generate_date_ranges('2023')

    def test_enrich_date_time_oneshot(self):
        """
        Tests that `_enrich_date_time` returns a dataframe with enriched datetime columns.
        """
        sample_weather_df = pd.DataFrame([sample_weather_data_historic])
        enriched_weather_df = _enrich_date_time(sample_weather_df)
        self.assertIn("record_start_date", enriched_weather_df.columns)
        self.assertEqual(enriched_weather_df["record_start_date"][0].year, 2024)

    def test_enrich_date_time_edge(self):
        """
        Tests that `_enrich_date_time` raises error for invalid inputs.
        """
        # Invalid Data
        weather_data_historic_bad = {
            "valid_time_gmt": 1672531200.00,
            "expire_time_gmt": 1672544800,
            "day_ind": "N",
            "temp": 20,
            "dewPt": 15,
            "rh": 75,
            "wdir_cardinal": "N",
            "gust": 10,
            "wspd": 5,
            "pressure": 1013,
            "precip_hrly": 0,
            "wx_phrase": "Clear",
        }

        sample_weather_df = pd.DataFrame([weather_data_historic_bad])
        with self.assertRaises(TypeError):
            _enrich_date_time(sample_weather_df)

        # Missing Data
        weather_data_historic_bad = {
            "expire_time_gmt": 1672544800,
            "day_ind": "N",
            "temp": 20,
            "dewPt": 15,
            "rh": 75,
            "wdir_cardinal": "N",
            "gust": 10,
            "wspd": 5,
            "pressure": 1013,
            "precip_hrly": 0,
            "wx_phrase": "Clear",
        }

        sample_weather_df = pd.DataFrame([weather_data_historic_bad])
        with self.assertRaises(ValueError):
            _enrich_date_time(sample_weather_df)

    def test_clean_historic_weather_data_oneshot(self):
        """
        Tests that `_clean_historic_weather_data` adds new columns to the dataframe .
        """
        refined_data = _clean_historic_weather_data(
            pd.DataFrame([sample_weather_data_historic]),
            'SEA',
            ['valid_time_gmt', 'expire_time_gmt', 'day_ind'])

        self.assertIn("record_start_date", refined_data.columns)
        self.assertEqual(refined_data["record_start_date"][0].year, 2024)

    def test_clean_historic_weather_data_edge(self):
        """
        Tests that `_clean_historic_weather_data` raises error for invalid inputs.
        """
        with self.assertRaises(ValueError):
            _clean_historic_weather_data(
                pd.DataFrame([sample_weather_data_historic]),
                'SEA',
                ['valid_time_gmt', 'expire_time_gmt', 'DayNight'])

    def test_refine_forecasted_data_oneshot(self):
        """
        Tests that `_refine_forecasted_data` adds new columns to the dataframe .
        """
        refined_data = _refine_forecasted_data(
            pd.DataFrame([sample_weather_data_forecasted]),
            ['validTimeUtc', 'expirationTimeUtc', 'temperature'])

        self.assertIn("record_start_date", refined_data.columns)
        self.assertEqual(refined_data["record_start_date"][0].year, 2024)

    def test_refine_forecasted_data_edge(self):
        """
        Tests that `_refine_forecasted_data` raises error for invalid inputs.
        """
        with self.assertRaises(ValueError):
            _refine_forecasted_data(
                pd.DataFrame([sample_weather_data_forecasted]),
                ['validTimeUtc', 'expirationTimeUtc', 'TEMP'])

    def test_get_historic_weather_data_smoke(self):
        """
        Tests that `get_historic_weather_data` works without errors for valid inputs.
        """
        # Sample airport data
        airports_df = pd.DataFrame({'Airport Code': ['BIL', 'SEA']})

        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._generate_date_ranges') as mock_generate_dates, \
                mock.patch('pandas.DataFrame.to_csv'):
            # Mock _generate_date_ranges to return a list of date ranges
            mock_generate_dates.return_value = [
                {"year": 2023, "month": 1, "start_date": "20230101", "end_date": "20230131"},
                {"year": 2023, "month": 2, "start_date": "20230201", "end_date": "20230228"}
            ]

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "metadata": {
                    "language": "en-US",
                    "transaction_id": "1709947547415:dd54786bfab23fca11a53b9a9c2878a5",
                    "version": "1",
                    "location_id": "KBIL:9:US",
                    "units": "e",
                    "expire_time_gmt": 1709951147,
                    "status_code": 200
                },
                "observations": [
                    {
                        "key": "KBIL",
                        "class": "observation",
                        "expire_time_gmt": 1641030780,
                        "obs_id": "KBIL",
                        "obs_name": "Billings",
                        "valid_time_gmt": 1641023580,
                        "day_ind": "N",
                        "temp": -11,
                        "wx_icon": 33,
                        "icon_extd": 3300,
                        "wx_phrase": "Fair",
                        "pressure_tend": "",
                        "pressure_desc": "",
                        "dewPt": -16,
                        "heat_index": -11,
                        "rh": 78,
                        "pressure": 26.25,
                        "vis": 10,
                        "wc": -30,
                        "wdir": 220,
                        "wdir_cardinal": "SW",
                        "gust": "",
                        "wspd": 10,
                        "max_temp": "",
                        "min_temp": "",
                        "precip_total": "",
                        "precip_hrly": 0,
                        "snow_hrly": "",
                        "uv_desc": "Low",
                        "feels_like": -30,
                        "uv_index": 0,
                        "qualifier": "",
                        "qualifier_svrty": "",
                        "blunt_phrase": "",
                        "terse_phrase": "",
                        "clds": "FEW",
                        "water_temp": "",
                        "primary_wave_period": "",
                        "primary_wave_height": "",
                        "primary_swell_period": "",
                        "primary_swell_height": "",
                        "primary_swell_direction": "",
                        "secondary_swell_period": "",
                        "secondary_swell_height": "",
                        "secondary_swell_direction": ""
                    }]}
            mock_get.return_value = mock_response

            # Call the function
            get_historic_weather_data(airports_df, 2023, 2023)
            self.assertTrue(True)

    def test_get_historic_weather_data_edge_years(self):
        """
        Tests that `get_historic_weather_data` raises error for invalid years.
        """

        airports_df = pd.DataFrame({'Airport Code': ['BIL', 'SEA']})

        with self.assertRaises(ValueError):
            get_historic_weather_data(airports_df, 2025, 2023)
        with self.assertRaises(ValueError):
            get_historic_weather_data(airports_df, -2023, 2023)
        with self.assertRaises(TypeError):
            get_historic_weather_data(airports_df, 2023, 2023.00)

    def test_get_historic_weather_data_edge_airports(self):
        """
        Tests that `get_historic_weather_data` raises error for invalid 'airports' data.
        """

        airports_df_1 = pd.DataFrame({'Airport Code 123': ['BIL', 'SEA']})
        airports_df_2 = ['BIL', 'SEA']

        with mock.patch('utils.weather._generate_date_ranges') as mock_generate_dates:
            mock_generate_dates.return_value = [
                {"year": 2023, "month": 1, "start_date": "20230101", "end_date": "20230131"},
                {"year": 2023, "month": 2, "start_date": "20230201", "end_date": "20230228"}
            ]

            with self.assertRaises(ValueError):
                get_historic_weather_data(airports_df_1, 2023, 2025)
            with self.assertRaises(TypeError):
                get_historic_weather_data(airports_df_2, 2023, 2025)

    def test_get_historic_weather_data_edge_response_1(self):
        """
        Tests that `get_historic_weather_data` handles error responses from API
        """

        airports_df = pd.DataFrame({'Airport Code': ['BIL', 'SEA']})

        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._generate_date_ranges') as mock_generate_dates, \
                mock.patch('pandas.DataFrame.to_csv'):

            # Mock _generate_date_ranges to return a list of date ranges
            mock_generate_dates.return_value = [
                {"year": 2023, "month": 1, "start_date": "20230101", "end_date": "20230131"},
                {"year": 2023, "month": 2, "start_date": "20230201", "end_date": "20230228"}
            ]

            # Mock a failure API response
            mock_response = mock.Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "metadata": {
                    "transaction_id": "1709954422494:62a0930670c953864da3f0ade2af1c80",
                    "status_code": 400
                },
                "success": False,
                "errors": [
                    {
                        "error": {
                            "code": "ILA-0001",
                            "message": "The location supplied is invalid."
                        }
                    }
                ]
            }
            mock_get.return_value = mock_response

            # Call the function
            get_historic_weather_data(airports_df, 2023, 2023)
            self.assertTrue(True)

    def test_get_historic_weather_data_edge_response_2(self):
        """
        Tests that `get_historic_weather_data` handles error responses from API
        """

        airports_df = pd.DataFrame({'Airport Code': ['BIL', 'SEA']})

        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._generate_date_ranges') as mock_generate_dates, \
                mock.patch('pandas.DataFrame.to_csv'):

            # Mock _generate_date_ranges to return a list of date ranges
            mock_generate_dates.return_value = [
                {"year": 2023, "month": 1, "start_date": "20230101", "end_date": "20230131"},
                {"year": 2023, "month": 2, "start_date": "20230201", "end_date": "20230228"}
            ]

            # Mock successful API response with missing data
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "metadata": {
                    "language": "en-US",
                    "transaction_id": "1709947547415:dd54786bfab23fca11a53b9a9c2878a5",
                    "version": "1",
                    "location_id": "KBIL:9:US",
                    "units": "e",
                    "expire_time_gmt": 1709951147,
                    "status_code": 200
                }}
            mock_get.return_value = mock_response

            # Call the function
            get_historic_weather_data(airports_df, 2023, 2023)
            self.assertTrue(True)

    def test_get_weather_forecast_oneshot(self):
        """
        Tests that `get_weather_forecast` works without errors for valid inputs.
        """
        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._refine_forecasted_data') as mock_refined_data:

            mock_refined_data.return_value = pd.DataFrame([sample_weather_data_historic])

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'validTimeUtc': [1709931638],  # 8th March 2024
                'expirationTimeUtc': [1710018038],
                'dayOrNight': ['N'],
                'temperature': [20],
                'temperatureDewPoint': [15],
                'relativeHumidity': [75],
                'windDirectionCardinal': ['N'],
                'windGust': [10],
                'windSpeed': [5],
                'pressureMeanSeaLevel': [1013],
                'wxPhraseShort': ['Clear']
            }
            mock_get.return_value = mock_response

            # Call the function
            forecast_df = get_weather_forecast('SEA', 1709931938)
            self.assertIn("temp", forecast_df.columns)
            self.assertEqual(forecast_df['temp'][0], 20)

    def test_get_weather_forecast_edge_invalid_input(self):
        """
        Tests that `get_weather_forecast` raises error for invalid inputs.
        """
        with self.assertRaises(TypeError):
            get_weather_forecast(123, 1709931938)
        with self.assertRaises(TypeError):
            get_weather_forecast('SEA', 1709931938.00)
        with self.assertRaises(ValueError):
            get_weather_forecast('SEA', -1709931938)

    def test_get_weather_forecast_edge_response_1(self):
        """
        Tests that `get_weather_forecast` raises error for failed API call
        """
        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._refine_forecasted_data') as mock_refined_data:

            mock_refined_data.return_value = pd.DataFrame([sample_weather_data_historic])

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "success": False,
                "errors": [
                    {
                        "code": "EAE:RNF-0001",
                        "message": "Requested resource icaoCode not found on the server."
                    }
                ],
                "metadata": {
                    "transaction_id": "1429140092945:1801695336",
                    "status_code": 404
                }
            }
            mock_get.return_value = mock_response

            with self.assertRaises(requests.HTTPError):
                get_weather_forecast('SEA', 1709931938)

    def test_get_weather_forecast_edge_response_2(self):
        """
        Tests that `get_weather_forecast` raises error for missing data in response
        """
        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._refine_forecasted_data') as mock_refined_data:

            mock_refined_data.return_value = pd.DataFrame([sample_weather_data_historic])

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'expirationTimeUtc': [1710018038],
                'dayOrNight': ['N'],
                'temperature': [20],
                'temperatureDewPoint': [15],
                'relativeHumidity': [75],
                'windDirectionCardinal': ['N'],
                'windGust': [10],
                'windSpeed': [5],
                'pressureMeanSeaLevel': [1013],
                'wxPhraseShort': ['Clear']
            }
            mock_get.return_value = mock_response

            with self.assertRaises(ValueError):
                get_weather_forecast('SEA', 1709931938)

    def test_get_weather_forecast_edge_response_3(self):
        """
        Tests that `get_weather_forecast` raises error for missing data in response
        """
        with mock.patch('requests.get') as mock_get:

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'validTimeUtc': [1709931638],  # 8th March 2024
                'expirationTimeUtc': [1710018038],
                'dayOrNight': ['N'],
                'temperature': [20],
            }
            mock_get.return_value = mock_response

            with self.assertRaises(ValueError):
                get_weather_forecast('SEA', 1709931938)

    def test_get_weather_forecast_edge_data_unavailable(self):
        """
        Tests that `get_weather_forecast` works without errors for valid inputs.
        """
        with mock.patch('requests.get') as mock_get, \
                mock.patch('utils.weather._refine_forecasted_data') as mock_refined_data:

            mock_refined_data.return_value = pd.DataFrame([sample_weather_data_historic])

            # Mock successful API response
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'validTimeUtc': [1709931638],  # 8th March 2024
                'expirationTimeUtc': [1710018038],
                'dayOrNight': ['N'],
                'temperature': [20],
                'temperatureDewPoint': [15],
                'relativeHumidity': [75],
                'windDirectionCardinal': ['N'],
                'windGust': [10],
                'windSpeed': [5],
                'pressureMeanSeaLevel': [1013],
                'wxPhraseShort': ['Clear']
            }
            mock_get.return_value = mock_response

            with self.assertRaises(ValueError):
                get_weather_forecast('SEA', 1720018038)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeather)
    _ = unittest.TextTestRunner().run(suite)
