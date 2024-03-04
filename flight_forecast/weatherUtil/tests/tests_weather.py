import unittest
import pandas as pd
from datetime import date
from unittest.mock import patch, MagicMock

from weather.weather import (
    get_month_range
)

class TestWeather(unittest.TestCase):

    def test_get_month_range(self):
        start_date, end_date = get_month_range(2023, 1)
        self.assertEqual(start_date, date(2023, 1, 1))
        self.assertEqual(end_date, date(2023, 1, 31))

        start_date, end_date = get_month_range(2024, 2)
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

if (__name__ == '__main__'):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeather)
    _ = unittest.TextTestRunner().run(suite)