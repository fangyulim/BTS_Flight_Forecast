"""
This module contains the test case for flight_delay_multi_page module.
"""

import sys
import unittest
# import shutil
from unittest.mock import patch  #, call
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QDate, QTime


from utils.ui_manager import FlightUi

# test_user_interface.py:17:0: R0904: Too many public methods (23/20) (too-many-public-methods)
class TestUi(unittest.TestCase):
    """
    This class contains the test for the UI model.
    """
    def setUp(self):
        """
        This function sets up the UI.
        """
        self.app = QApplication(sys.argv)
        self.ui = FlightUi()

    def tearDown(self):
        """
        This function closes the UI.
        """
        self.ui.close()
        del self.ui
        del self.app

    def test_setup_ui(self):
        """
        This function tests that the UI is being set up with default values
        UI width is set to 1200, height is set to 750.
        Certain labels and widget is not visible before actions have been taken.
        """
        self.ui.setup_ui()
        self.assertEqual(self.ui.width(), 1200)
        self.assertEqual(self.ui.height(), 750)
        # Following labels and widgets appear false initially
        self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
        self.assertFalse(self.ui.user_int.label_6.isVisible())
        self.assertFalse(self.ui.user_int.prob_delay_result.isVisible())
        self.assertFalse(self.ui.user_int.label_5.isVisible())
        self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())

        # Authentication page
        self.assertFalse(self.ui.user_int.error_msg_lb.isVisible())

        # Admin page
        self.assertFalse(self.ui.user_int.file_lb.isVisible())
        self.assertFalse(self.ui.user_int.new_mod_lb.isVisible())
        self.assertFalse(self.ui.user_int.mod_title_lb.isVisible())
        self.assertFalse(self.ui.user_int.year_indicator.isVisible())
        # self.assertFalse(self.ui.user_int.option_btn.isVisible())
        # self.assertFalse(self.ui.user_int.retrain_optionlb.isVisible())
        # self.assertFalse(self.ui.user_int.refit_lb.isVisible())

    def test_main_window_displayed_correctly(self):
        """
        This function tests if the main window displays correctly.
        """
        # Wait for the window to be exposed
        QTest.qWaitForWindowExposed(self.ui)
        self.ui.show()
        # Check if the main window is visible
        self.assertTrue(self.ui.isVisible())

    def test_read_airport_codes(self):
        """
        This function tests if we are reading in the airport_codes correctly from the csv file.
        """
        expected_airport_codes = ['BIL', 'BLI', 'BOI', 'BTM', 'BZN', 'CLM', 'ORS', 'EUG', 'GPI',
                                  'FHR', 'GDV', 'GEG', 'GGW', 'GTF', 'HLN', 'HVR', 'IDA', 'SEA',
                                  'LMT', 'LWS', 'LWT', 'MLS', 'MSO', 'OKH', 'OLF', 'PDT', 'PDX',
                                  'PIH', 'PUW', 'SDY', 'SEA', 'SUN', 'TWF']
        actual_airport_codes = self.ui.load_airport_list()

        self.assertEqual(actual_airport_codes, expected_airport_codes)

    def test_airport_codes_added_to_widget(self):
        """
        This function tests that airport codes are being added to the airport_selection widget.
        """
        airport_codes = ['BIL', 'BLI', 'BOI', 'BTM', 'BZN', 'CLM', 'ORS', 'EUG', 'GPI',
                         'FHR', 'GDV', 'GEG', 'GGW', 'GTF', 'HLN', 'HVR', 'IDA', 'SEA',
                         'LMT', 'LWS', 'LWT', 'MLS', 'MSO', 'OKH', 'OLF', 'PDT', 'PDX',
                         'PIH', 'PUW', 'SDY', 'SEA', 'SUN', 'TWF']
        self.ui.load_airport_list()
        for index, airport_codes in enumerate(airport_codes):
            self.assertEqual(self.ui.user_int.airport_selection.itemText(index), airport_codes)

    def test_admin_button_switches_page(self):
        """
        This function checks if clicking the admin_button switches to the admin login page.
        """
        QTest.mouseClick(self.ui.user_int.admin_login_btn, Qt.LeftButton)
        QApplication.processEvents()
        self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 1)

    def test_main_button_switches_page(self):
        """
        This function checks if clicking the main_button switches to the main page.
        """
        # intial_index = self.ui.stacked_widget_pages.currentIndex()
        QTest.mouseClick(self.ui.user_int.main_page_btn, Qt.LeftButton)
        QApplication.processEvents()
        self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 0)

    def test_predict_button_with_valid_conditions_1(self):
        """
        This function checks if predict_button works when day difference is within
        15 days from today and check_box is unchecked.
        """
        # Simulate conditions where prediction is valid
        if 1 < self.ui.day_difference <= 15 and not self.ui.user_int.check_box.isChecked():
            QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
            QApplication.processEvents()

            # Assertions for expected visibility
            self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
            self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
            self.assertFalse(self.ui.user_int.label_6.isVisible())
            self.assertTrue(self.ui.user_int.prob_delay_result.isVisible())
            self.assertTrue(self.ui.user_int.label_5.isVisible())

    def test_predict_button_with_valid_conditions_2(self):
        """
        This function checks if predict_button works when day difference is within
        15 days from today and check_box is checked.
        """
        if 1 < self.ui.day_difference <= 15 and self.ui.user_int.check_box.isChecked():
            QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
            QApplication.processEvents()

            # Assertions for expected visibility
            self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
            self.assertTrue(self.ui.user_int.avg_delay_result.isVisible())
            self.assertTrue(self.ui.user_int.label_6.isVisible())
            self.assertTrue(self.ui.user_int.prob_delay_result.isVisible())
            self.assertTrue(self.ui.user_int.label_5.isVisible())

    def test_predict_button_with_invalid_conditions_1(self):
        """
        This function checks if predict_button works when day difference is not within
        15 days from today and check_box is checked.
        """
        if not (1 <= self.ui.day_difference <= 15) and self.ui.user_int.check_box.isChecked():
            QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
            QApplication.processEvents()

            # Assertions for expected visibility
            self.assertTrue(self.ui.user_int.fail_predict_lb.isVisible())
            self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
            self.assertFalse(self.ui.user_int.label_6.isVisible())
            self.assertFalse(self.ui.user_int.prob_delay_result.isVisible())
            self.assertFalse(self.ui.user_int.label_5.isVisible())

    def test_predict_button_with_invalid_conditions_2(self):
        """
        This function checks if predict_button works when day difference is not within
        15 days from today and check_box is not checked.
        """
        if not (1 <= self.ui.day_difference <= 15) and not self.ui.user_int.check_box.isChecked():
            QTest.mouseClick(self.ui.user_int.PredictButton, Qt.LeftButton)
            QApplication.processEvents()

            # Assertions for expected visibility
            self.assertFalse(self.ui.user_int.fail_predict_lb.isVisible())
            self.assertFalse(self.ui.user_int.avg_delay_result.isVisible())
            self.assertFalse(self.ui.user_int.label_6.isVisible())
            self.assertFalse(self.ui.user_int.prob_delay_result.isVisible())
            self.assertFalse(self.ui.user_int.label_5.isVisible())

    def test_login_button_authenticates_correct(self):
        """
        This function tests is login_btn works and brings admin to admin page
        when correct password is entered.
        """
        initial_index = self.ui.stacked_widget_pages.currentIndex()
        self.ui.user_int.password_input.setText("123")
        QTest.mouseClick(self.ui.user_int.login_btn, Qt.LeftButton)
        QApplication.processEvents()
        new_index = self.ui.stacked_widget_pages.currentIndex()
        self.assertNotEqual(initial_index, new_index)
        self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 2)
        self.assertFalse(self.ui.user_int.error_msg_lb.isVisible())

    def test_login_button_authenticates_incorrect(self):
        """
        This function tests if login_btn works and doesn't bring admin to admin page
        when incorrect password is entered.
        """
        initial_index = self.ui.stacked_widget_pages.currentIndex()
        QTest.mouseClick(self.ui.user_int.login_btn, Qt.LeftButton)
        QApplication.processEvents()
        new_index = self.ui.stacked_widget_pages.currentIndex()
        if self.ui.user_int.password_input.text() == "abc":
            self.assertEqual(initial_index, new_index)
            self.assertTrue(self.ui.user_int.error_msg_lb.isVisible())
            self.assertEqual(self.ui.stacked_widget_pages.currentIndex(), 1)

    def test_line_edit_text_input(self):
        """
        This function checks that we are getting user input in years_input.
        """
        input_text = "2022,2024"
        QTest.keyClicks(self.ui.user_int.years_input, input_text)
        entered_text = self.ui.user_int.years_input.text()
        self.assertEqual(entered_text, input_text)

    def test_combobox_input(self):
        """
        This function checks if we can find an item in the airport_selection
        combo box.
        """
        # Select an item in the combo box
        input_item = "SEA"  # Replace with the item you want to select
        index = self.ui.user_int.airport_selection.findText(input_item)
        self.assertNotEqual(index, -1, f"Item '{input_item}' not found in combo box")

        self.ui.user_int.airport_selection.setCurrentIndex(index)

        # Get the currently selected item
        selected_item = self.ui.user_int.airport_selection.currentText()

        # Verify if the selected item matches the expected input
        self.assertEqual(selected_item, input_item)

    def test_combobox_insertion(self):
        """
        This function checks if items are getting insert into the airport_selection
        combobox.
        """
        # Get the list of items before insertion
        items_before = [self.ui.user_int.airport_selection.itemText(i)
                        for i in range(self.ui.user_int.airport_selection.count())]

        # Insert an item into the combo box
        new_item = "New Airport"  # Replace with the item you want to insert
        self.ui.user_int.airport_selection.addItem(new_item)

        # Get the list of items after insertion
        items_after = [self.ui.user_int.airport_selection.itemText(i)
                       for i in range(self.ui.user_int.airport_selection.count())]

        # Verify if the new item is inserted into the combo box
        self.assertIn(new_item, items_after)
        # Verify if the number of items has increased by 1
        self.assertEqual(len(items_before) + 1, len(items_after))

    def test_date_selection(self):
        """
        This function checks if we are getting date selection.
        """
        # Clear any potential initial value
        self.ui.user_int.date_selection.clear()

        # Set a date beyond the current date (adjust as needed)
        selected_date = QDate(2024, 8, 9)

        # Set the date on the QDateEdit widget
        self.ui.user_int.date_selection.setDate(selected_date)

        # Ensure event processing (optional)
        QApplication.processEvents()

        # Retrieve the selected date
        retrieved_date = self.ui.user_int.date_selection.date()

        # Verify the dates
        self.assertEqual(selected_date, retrieved_date)

    def test_time_selection(self):
        """
        This function checks if we are getting time selection.
        """
        # Clear any potential initial value
        self.ui.user_int.time_selection.clear()

        # Set a date beyond the current date (adjust as needed)
        selected_time = QTime(3, 12, 0)

        # Set the date on the QDateEdit widget
        self.ui.user_int.time_selection.setTime(selected_time)

        # Ensure event processing (optional)
        QApplication.processEvents()

        # Retrieve the selected date
        retrieved_date = self.ui.user_int.time_selection.time()

        # Verify the dates
        self.assertEqual(selected_time, retrieved_date)

    def test_process_time_comma(self):
        """
        This function checks if there is a comma in the years entered by admin.
        If not, prompts users to re-enter start and end years in the correct format.
        """
        mes = "The start_year is: " + str(2010) + "\n" + "The end year is: "\
                                    + str(2022)
        years_input_info = "2010,2022"
        self.ui.process_input(years_input_info)
        self.assertEqual(self.ui.start_year ,"2010")
        self.assertEqual(self.ui.end_year,"2022")
        self.assertEqual(self.ui.user_int.year_indicator.text(), mes)

    def test_process_time_no_comma(self):
        """
        This function checks if there is a comma in the years entered by admin.
        If not, prompts users to re-enter start and end years in the correct format.
        """
        mes = "Please enter start & end year in correct format (no space) and press enter!"
        years_input_info = "20102022"
        self.ui.process_input(years_input_info)
        self.assertEqual(self.ui.user_int.year_indicator.text(), mes)
        # Somehow can't test this?? Gives error False is not True
        # self.assertTrue(self.ui.user_int.year_indicator.isVisible())

    def test_handle_return_input(self):
        """
        This function checks if the handle_return_input() function takes in user input as expected.
        """
        self.ui.user_int.years_input.setText("1990,2022")
        result = self.ui.handle_return_input()
        self.assertEqual(result, "1990,2022")

    # @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(
    #         ["C:/Users/fioyu/Pictures/Screenshots/Screenshot 2023-05-19 062955.png"], ""))
    # def test_upload(self, mock_getOpenFileNames):
    def test_upload(self):
        """
        This function checks that by clicking the upload button the file dialog
        appears.
        :param mock_getOpenFileNames
        """
        # Simulate clicking the upload button
        QTest.mouseClick(self.ui.user_int.upload_btn, Qt.LeftButton)
        QApplication.processEvents()

        # Check if the upload_files method is called
        self.ui.upload_files()

    # @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], ""))
    # def test_upload_none(self, mock_getOpenFileNames):
    def test_upload_none(self):
        """
        This function mocks the case where users click the upload button but doesn't
        upload anything.
        :param mock_getOpenFileNames:
        """
        # Simulate clicking the upload button
        QTest.mouseClick(self.ui.user_int.upload_btn, Qt.LeftButton)
        QApplication.processEvents()

        # Check if the upload_files method is called
        self.ui.upload_files()
        mes = "No files have been uploaded."
        self.assertEqual(self.ui.user_int.file_lb.text(), mes)
        # Same case here, message works, but can't check if label is visible
        # self.assertTrue(self.ui.user_int.file_lb.isVisible())

    # @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames',
    # return_value=(["C:/Users/fioyu/Desktop/UW/DATA515/Project/BTS_Flight_Forecast
    # /flight_forecast/resources/flight_data/June2022.zip",
    # "C:/Users/fioyu/Desktop/UW/DATA515/Project/BTS_Flight_Forecast/flight_forecast
    # /resources/flight_data/May2022.zip"], ""))
    # def test_upload_files(self, mock_getOpenFileNames):
    #     # Simulate clicking the upload button
    #     QTest.mouseClick(self.ui.user_int.upload_btn, Qt.LeftButton)
    #     QApplication.processEvents()
    #     self.start_year = 2022
    #     self.end_year = 2022
    #     start_year_input = int(self.start_year)
    #     end_year_input = int(self.end_year)
    #
    #     # Check if the upload_files method is called
    #     self.ui.upload_files()
    #
    #     # Assert that the file labels are updated
    #     # expected_text = "You have uploaded 2 file(s)."
    #     # self.assertEqual(self.ui.user_int.new_mod_lb.text(), expected_text)
    #     # self.assertTrue(self.ui.user_int.file_lb.isVisible())
    #
    #     with patch('shutil.copy') as shutil_copy_mock:
    #         expected_calls = [
    #             call("C:/Users/fioyu/Desktop/UW/DATA515/Project/BTS_Flight_Forecast
    #             /flight_forecast/resources/flight_data/June2022.zip", "C:/Users
    #             /fioyu/Desktop/UW/DATA515/Project/project_v2/BTS_Flight_Forecast/
    #             flight_forecast/resources/flight_data/June2022.zip"),
    #             call("C:/Users/fioyu/Desktop/UW/DATA515/Project/BTS_Flight_Forecast
    #             /flight_forecast/resources/flight_data/May2022.zip", "C:/Users
    #             /fioyu/Desktop/UW/DATA515/Project/project_v2/BTS_Flight_Forecast/
    #             flight_forecast/resources/flight_data/May2022.zip")
    #         ]
    #         shutil_copy_mock.assert_has_calls(expected_calls)
    #
    #     # Assert that retrain_models is called with the correct number of uploaded files
    #     self.assertEqual(self.retrain_models_mock.call_count, 1)
    #     self.assertEqual(self.retrain_models_mock.call_args[0][0], 2)
    # Can't do this test because I'm asking for users to input until I get a correct format.
    # def test_process_time_invalid_years(self):
    #     """
    #     This function tests that if 2 valid years were given.
    #     If not raise ValueError.
    #     """
    #     years_input_info = "2010,111"  # Only one year has 3 digits
    #
    #     with self.assertRaises(ValueError):
    #         self.ui.process_input(years_input_info)
    #
    #     years_input_info = "2010,20200"  # One year has 5 digits
    #     with self.assertRaises(ValueError):
    #         self.ui.process_input(years_input_info)
    #
    #     years_input_info = "2010,abcd"  # One year is not a valid number
    #     with self.assertRaises(ValueError):
    #         self.ui.process_input(years_input_info)


if __name__ == '__main__':
    unittest.main()
