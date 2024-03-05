"""
This module contains unit tests for various function defined in the `weather` module.
"""

import unittest
from datetime import date
from unittest import mock

import pandas as pd

from weather.weather import (
    get_month_range,
    generate_date_ranges,
    enrich_date_time,
    clean_historic_weather_data,
    refine_forecasted_data
)

sample_weather_data_historic = {
    "valid_time_gmt": 1672531200,
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

sample_weather_data_forecasted = {
    'validTimeUtc': 1672531200,
    'expirationTimeUtc': 1672544800,
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

    def test_get_month_range(self):
        """
        Tests that `get_month_range` returns the correct start and end dates for a month.
        """

        start_date, end_date = get_month_range(2023, 1)
        self.assertEqual(start_date, date(2023, 1, 1))
        self.assertEqual(end_date, date(2023, 1, 31))

        start_date, end_date = get_month_range(2024, 2)
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

    def test_generate_date_ranges(self):

        """
        Tests that `generate_date_ranges` returns the correct list of start and end dates per month.
        """
        date_ranges = generate_date_ranges([2023, 2024])
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

    def test_enrich_date_time(self):
        """
        Tests that `enrich_date_time` returns a dataframe with enriched datetime columns.
        """
        sample_weather_df = pd.DataFrame([sample_weather_data_historic])
        enriched_weather_df = enrich_date_time(sample_weather_df)
        self.assertIn("start_year", enriched_weather_df.columns)
        self.assertEqual(enriched_weather_df["start_year"][0], 2023)

    @mock.patch("requests.get")
    def test_clean_historic_weather_data(self, mock_get):
        """
        Tests that `clean_historic_weather_data` returns adds new columns to the dataframe .
        """
        mock_response = mock.Mock(status_code=200)
        mock_response.json = {"observations": [sample_weather_data_historic]}
        mock_get.return_value = mock_response

        cleaned_data = clean_historic_weather_data(
            pd.DataFrame([sample_weather_data_historic]), "SEA", ["valid_time_gmt", "expire_time_gmt"]
        )

        self.assertEqual(cleaned_data["location_id"][0], "SEA")
        self.assertIn("start_year", cleaned_data.columns)

    def test_refine_forecasted_data(self):
        refined_data = refine_forecasted_data(pd.DataFrame([sample_weather_data_forecasted]))
        self.assertEqual(refined_data["day_ind"][0], sample_weather_data_forecasted['dayOrNight'])
        self.assertIn("start_hour_gmt", refined_data.columns)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeather)
    _ = unittest.TextTestRunner().run(suite)
