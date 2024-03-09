# """
# This module contains the test case for flight_delay_multi_page module.
# """
# # import csv
# import sys
# # import shutil
# # from datetime import datetime
# # import os
# import unittest
# # from unittest.mock import patch
# # import pandas as pd
# # from PyQt5 import uic
# from PyQt5.QtTest import QTest  # QSignalSpy
# from PyQt5.QtWidgets import QApplication  # , QMainWindow, QFileDialog, QWidget,QInputDialog
# from PyQt5.QtCore import Qt, QDate, QTime  # QDateTime, QTimeZone,
# # from utils.weather import (
# #     get_weather_forecast,
# #     get_historic_weather_data
# # )
# # from utils.data_combination_1 import create_dataset
# # from utils.delay_modelling_2 import (
# #     create_model_from_dataset,
# #     predict_delay_probability,
# #     get_classifier_metrics,
# #     predict_delay_severity,
# #     get_regressor_metrics
# # )
# from utils.flight_delay_multi_page_ui import FlightUi
#
#
# class TestUi(unittest.TestCase):
#     """
#     This class contains the test for the UI model.
#     """
#     def setUp(self):
#         """
#         This function sets up the UI.
#         """
#         self.app = QApplication(sys.argv)
#         self.ui = FlightUi()
#
#     def tearDown(self):
#         """
#         This function closes the UI.
#         """
#         self.ui.close()
#         del self.ui
#         del self.app
#
#     def test_main_window_displayed_correctly(self):
#         """
#         This function tests if the main window displays correctly.
#         :return:
#         """
#         # Wait for the window to be exposed
#         QTest.qWaitForWindowExposed(self.ui)
#         self.ui.show()
#         # Check if the main window is visible
#         self.assertTrue(self.ui.isVisible())
#
#     def test_admin_button_switches_page(self):
#         """
#         This function checks if clicking the admin_button switches to the admin login page.
#         """
#         QTest.mouseClick(self.ui.user_int.admin_login_btn, Qt.LeftButton)
#         QApplication.processEvents()
#         self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 1)
#
#     def test_main_button_switches_page(self):
#         """
#         This function checks if clicking the main_button switches to the main page.
#         """
#         # intial_index = self.ui.stacked_widget_pages.currentIndex()
#         QTest.mouseClick(self.ui.user_int.main_page_btn, Qt.LeftButton)
#         QApplication.processEvents()
#         self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 0)
#
#     def test_predict_button_with_valid_conditions_1(self):
#         """
#         This function checks if predict_button works when day difference is within
#         15 days from today and check_box is unchecked.
#         """
#         # Simulate conditions where prediction is valid
#         if 1 < self.ui.day_difference <= 15 and not self.ui.user_int.check_box.isChecked():
#             QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
#             QApplication.processEvents()
#
#             # Assertions for expected visibility
#             self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
#             self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
#             self.assertFalse(self.ui.user_int.label_6.isVisible())
#             self.assertTrue(self.ui.user_int.prob_delay_result.isVisible())
#             self.assertTrue(self.ui.user_int.label_5.isVisible())
#
#     def test_predict_button_with_valid_conditions_2(self):
#         """
#         This function checks if predict_button works when day difference is within
#         15 days from today and check_box is checked.
#         """
#         if 1 < self.ui.day_difference <= 15 and self.ui.user_int.check_box.isChecked():
#             QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
#             QApplication.processEvents()
#
#             # Assertions for expected visibility
#             self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
#             self.assertTrue(self.ui.user_int.avg_delay_result.isVisible())
#             self.assertTrue(self.ui.user_int.label_6.isVisible())
#             self.assertTrue(self.ui.user_int.prob_delay_result.isVisible())
#             self.assertTrue(self.ui.user_int.label_5.isVisible())
#
#     def test_predict_button_with_invalid_conditions_1(self):
#         """
#         This function checks if predict_button works when day difference is not within
#         15 days from today and check_box is checked.
#         """
#         if not (1 <= self.ui.day_difference <= 15) and self.ui.user_int.check_box.isChecked():
#             QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
#             QApplication.processEvents()
#
#             # Assertions for expected visibility
#             self.assertTrue(self.ui.user_int.fail_predict_lb.isVisible())
#             self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
#             self.assertFalse(self.ui.user_int.label_6.isVisible())
#             self.assertFalse(self.ui.user_int.prob_delay_result.isVisible())
#             self.assertFalse(self.ui.user_int.label_5.isVisible())
#
#     def test_predict_button_with_invalid_conditions_2(self):
#         """
#         This function checks if predict_button works when day difference is not within
#         15 days from today and check_box is not checked.
#         """
#         if not (1 <= self.ui.day_difference <= 15) and not self.ui.user_int.check_box.isChecked():
#             QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
#             QApplication.processEvents()
#
#             # Assertions for expected visibility
#             self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
#             self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
#             self.assertFalse(self.ui.user_int.label_6.isVisible())
#             self.assertFalse(self.ui.user_int.prob_delay_result.isVisible())
#             self.assertFalse(self.ui.user_int.label_5.isVisible())
#
#     def test_login_button_authenticates(self):
#         """
#         This function tests is login_btn works and brings admin to admin page
#         when correct password is entered.
#         """
#         initial_index = self.ui.stacked_widget_pages.currentIndex()
#         QTest.mouseClick(self.ui.user_int.login_btn, Qt.LeftButton)
#         QApplication.processEvents()
#         new_index = self.ui.stacked_widget_pages.currentIndex()
#         if self.ui.user_int.password_input.text() == "123":
#             self.assertNotEqual(initial_index, new_index)
#         else:
#             self.assertEqual(initial_index, new_index)
#
#     def test_line_edit_text_input(self):
#         """
#         This function checks that we are getting user input in years_input.
#         """
#         input_text = "2022,2024"
#         QTest.keyClicks(self.ui.user_int.years_input, input_text)
#         entered_text = self.ui.user_int.years_input.text()
#         self.assertEqual(entered_text, input_text)
#
#     def test_combobox_input(self):
#         """
#         This function checks if we can find an item in the airport_selection
#         combo box.
#         """
#         # Select an item in the combo box
#         input_item = "SEA"  # Replace with the item you want to select
#         index = self.ui.user_int.airport_selection.findText(input_item)
#         self.assertNotEqual(index, -1, f"Item '{input_item}' not found in combo box")
#
#         self.ui.user_int.airport_selection.setCurrentIndex(index)
#
#         # Get the currently selected item
#         selected_item = self.ui.user_int.airport_selection.currentText()
#
#         # Verify if the selected item matches the expected input
#         self.assertEqual(selected_item, input_item)
#
#     def test_combobox_insertion(self):
#         """
#         This function checks if items are getting insert into the airport_selection
#         combobox.
#         """
#         # Get the list of items before insertion
#         items_before = [self.ui.user_int.airport_selection.itemText(i)
#                         for i in range(self.ui.user_int.airport_selection.count())]
#
#         # Insert an item into the combo box
#         new_item = "New Airport"  # Replace with the item you want to insert
#         self.ui.user_int.airport_selection.addItem(new_item)
#
#         # Get the list of items after insertion
#         items_after = [self.ui.user_int.airport_selection.itemText(i)
#                        for i in range(self.ui.user_int.airport_selection.count())]
#
#         # Verify if the new item is inserted into the combo box
#         self.assertIn(new_item, items_after)
#         # Verify if the number of items has increased by 1
#         self.assertEqual(len(items_before) + 1, len(items_after))
#
#     def test_date_selection(self):
#         """
#         This function checks if we are getting date selection.
#         """
#         # Clear any potential initial value
#         self.ui.user_int.date_selection.clear()
#
#         # Set a date beyond the current date (adjust as needed)
#         selected_date = QDate(2024, 8, 9)
#
#         # Set the date on the QDateEdit widget
#         self.ui.user_int.date_selection.setDate(selected_date)
#
#         # Ensure event processing (optional)
#         QApplication.processEvents()
#
#         # Retrieve the selected date
#         retrieved_date = self.ui.user_int.date_selection.date()
#
#         # Verify the dates
#         self.assertEqual(selected_date, retrieved_date)
#
#     def test_time_selection(self):
#         """
#         This function checks if we are getting time selection.
#         """
#         # Clear any potential initial value
#         self.ui.user_int.time_selection.clear()
#
#         # Set a date beyond the current date (adjust as needed)
#         selected_time = QTime(3, 12, 0)
#
#         # Set the date on the QDateEdit widget
#         self.ui.user_int.time_selection.setTime(selected_time)
#
#         # Ensure event processing (optional)
#         QApplication.processEvents()
#
#         # Retrieve the selected date
#         retrieved_date = self.ui.user_int.time_selection.time()
#
#         # Verify the dates
#         self.assertEqual(selected_time, retrieved_date)
#
# # Verify that components are displaying correctly
# # Check if buttons, labels, dropdowns, and input fields are functional.
# # Test UI layout is consistent??
#
# # Test navigation between different pages.
# # Verify clicking on buttons switches to the correct page.
# # Check if navigating back and forth works as expected.
#
# # Test input validation for all input fields.
#
# # Test authentication with invalid credentials.
# # Test user is redirected to admin page upon successful authentication
# # Test appropriate error messages are displayed for failed attempts.
#
# # Test file upload functionality for one or multiple files.
# # Test correct files are uploaded and processed.
# # Check if error message displayed.
#
# # Test prediction by providing valid input.
# # Verify displaying correctly
# # Check if UI updated based on user selection
#
# # Test model retraining functionality by selecting retrain option.
# # Verify that retrained is successful and relevant feedback provided.
#
# # Edge Cases
# # Boundary values, empty inputs, or extreme scenarios
#
#
# if __name__ == '__main__':
#     unittest.main()
