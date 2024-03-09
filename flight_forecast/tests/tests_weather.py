"""
This module contains unit tests for various function defined in the `weather` module.
"""

import unittest
from datetime import date

import pandas as pd

from utils.weather import (
    _get_month_range,
    _generate_date_ranges,
    _enrich_date_time,
    _clean_historic_weather_data,
    _refine_forecasted_data
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeather)
    _ = unittest.TextTestRunner().run(suite)
