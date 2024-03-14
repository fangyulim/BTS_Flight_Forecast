"""
This module constructs a two page user interface, links api calls and produce predictions.

The first page allows users to selection airport code, date, and if they want
a prediction of delay severity, or just delay prediction.

The second page allows admin to upload more data and retrain the model.
Comments: I ended up not putting state and airport name in option because
not all airports have a name.

To use this module, please use command: python -m utils.flight_delay_multi_page_ui in terminal.
To run using IDE, please change file paths.
On the admin page, please enter start end year before uploading.
"""
import csv
import sys
import shutil
from datetime import datetime
import os

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QDateTime, QTimeZone
from . import weather
from . import data_processing
from . import delay_predictor

# GUI file
QT_CREATOR_FILE = 'resources/flight_delay_multi_page.ui'
ui_main_window, QtBaseClass = uic.loadUiType(QT_CREATOR_FILE)
AIRPORT_FOLDER_PATH = "resources/flight_data"
WEATHER_FOLDER_PATH = "resources/generated/weather_data"
PICKLE_FOLDER_PATH = "resources/generated/pickles"


class FlightUi(QMainWindow):
    """
    This class initializes the GUI and the widgets.
    """

    def __init__(self):
        """
        function documentation: This function sets up the windows and actions for specific changes
        """
        super().__init__()
        self.user_int = ui_main_window()
        self.user_int.setupUi(self)
        self.setup_ui()

        # Instantiated stacked widget and set default page to be main page(user).
        self.stacked_widget_pages = self.user_int.stacked_widget
        self.stacked_widget_pages.setCurrentIndex(0)

        self.start_year = None
        self.end_year = None
        self.num_uploaded = None
        self.day_difference = 0
        self.file_dialog = None
        self.setup_signal_slot_connection()

        # Centering labels
        label_main_page = self.user_int.main_page_lb
        label_main_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label_login_page = self.user_int.login_page_lb
        label_login_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label_admin_page = self.user_int.admin_page_lb
        label_admin_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Instantiating widgets and functions used on main page.
        self.load_airport_list()

    def setup_signal_slot_connection(self):
        """
        This function sets up signal slot connections.
        """
        # Moves to admin login page when " Admin Login" button is clicked
        self.user_int.admin_login_btn.clicked.connect(
            lambda: self.stacked_widget_pages.setCurrentIndex(1))
        # Moves to main page when "Main Page" button is clicked
        self.user_int.main_page_btn.clicked.connect(
            lambda: self.stacked_widget_pages.setCurrentIndex(0))
        self.user_int.PredictButton.clicked.connect(self.prediction)

        # Authentication page.
        self.user_int.login_btn.clicked.connect(self.authenticate)

        # Admin page.
        self.user_int.years_input.returnPressed.connect(self.handle_return_input)
        self.user_int.upload_btn.clicked.connect(self.upload_files)
        self.user_int.upload_btn.clicked.connect(self.retrain_models)

    def setup_ui(self):
        """
        This function sets up the UI.
        - Sets up the dimension of the UI.
        - Sets label/ widgets to not appear before user input.
        """
        width = 1200
        height = 750
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        # Main page
        self.user_int.avg_delay_result.setVisible(False)
        self.user_int.label_6.setVisible(False)
        self.user_int.prob_delay_result.setVisible(False)
        self.user_int.label_5.setVisible(False)
        self.user_int.fail_predict_lb.setVisible(False)
        self.user_int.success_lb.setVisible(False)

        # Authentication page
        self.user_int.error_msg_lb.setVisible(False)

        # Admin page
        self.user_int.file_lb.setVisible(False)
        self.user_int.new_mod_lb.setVisible(False)
        self.user_int.mod_title_lb.setVisible(False)
        # self.user_int.year_indicator.setVisible(False)
        self.user_int.option_btn.setVisible(False)
        # self.user_int.retrain_optionlb.setVisible(False)
        # self.user_int.refit_lb.setVisible(False)

    def load_airport_list(self):
        """
        This function displays the list of airports in the airport_selection widget.
        Currently, we are only using the list of airports in the pacific northwest.
        """

        # Reads in the airport codes from csv file.
        with open("resources/airport_codes.csv", "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # skips the header
            airport_codes = [row[0] for row in csv.reader(file)]

        # Clear the existing items in airport_selection widget
        self.user_int.airport_selection.clear()
        # Adds airport codes to the widget
        self.user_int.airport_selection.addItems(airport_codes)
        return airport_codes

    def prediction(self):
        """
        This function takes user input, fetches forecasted weather, runs prediction model and
        displays the predicted probability of delay or severity prediction.
        """
        # Obtaining user input
        date_input = self.user_int.date_selection.date()
        time_input = self.user_int.time_selection.time()
        airport_selected = self.user_int.airport_selection.currentText()

        # Combining data and time selection to convert to unit timestamp for weather forecast.
        date_time_selection = QDateTime(date_input, time_input, QTimeZone.utc())
        unix_timestamp = date_time_selection.toSecsSinceEpoch()

        # If selected day is within 15 days from today, then we are able to give a prediction
        date_selected = datetime(date_input.year(), date_input.month(), date_input.day())
        day_difference = int((date_selected - datetime.now()).days)
        if 0 <= day_difference <= 15:
            # 1. Create a list of relevant input columns, and a list of the inputs.
            relevant_user_input_columns = ['Year', 'Month', 'DayofMonth', 'Origin']
            user_input = [date_input.year(), date_input.month(), date_input.day(), airport_selected]

            # 2. Calls the get_weather_forecast() from weather module.
            forecast_weather_df = weather.get_weather_forecast(airport_selected, unix_timestamp)

            # 3. Create a list of relevant columns from df returned from step 2,
            # and a list of the corresponding values.
            forecast_weather_df_focused = forecast_weather_df[
                                          ['temp', 'dewPt', 'day_ind',
                                           'rh', 'wdir_cardinal', 'gust', 'wspd',
                                           'pressure', 'wx_phrase']]
            forecast_weather_columns = list(forecast_weather_df_focused.columns)
            forecast_weather_df_focused_values = forecast_weather_df_focused.values.tolist()[0]

            # 4. Create a combined dataframe of (1) and (3)
            combined_df = pd.DataFrame(columns=relevant_user_input_columns +
                                       forecast_weather_columns)
            combined_df.loc[0, :] = user_input+forecast_weather_df_focused_values

            # 5. Pass df from (4) into predict_delay_time() from data_modelling_2
            # if checkbox is selected. Displays result.
            if self.user_int.check_box.isChecked():

                severity_probability = delay_predictor.predict_delay_severity(combined_df)
                severity_prediction = f"The results are {severity_probability[0]:.2f}min."
                self.user_int.avg_delay_result.setText(severity_prediction)
                self.user_int.avg_delay_result.setVisible(True)
                self.user_int.label_6.setVisible(True)

            else:
                # Labels do not display if check box is not checked.
                self.user_int.avg_delay_result.setVisible(False)
                self.user_int.label_6.setVisible(False)

            # 6. Pass df from (4) into predict_delay_probability from data_modelling_2.
            # Displays result.
            delay_probability = delay_predictor.predict_delay_probability(combined_df)
            test = f"{delay_probability[0][0] * 100:.2f}"
            delay_prediction = f"The results are {test}%."
            self.user_int.prob_delay_result.setText(delay_prediction)
            self.user_int.prob_delay_result.setVisible(True)
            self.user_int.label_5.setVisible(True)
            self.user_int.fail_predict_lb.setVisible(False)

        else:
            # Displays fail_predict_lb label.
            # Does not display all other labels.
            self.user_int.fail_predict_lb.setVisible(True)
            self.user_int.prob_delay_result.setVisible(False)
            self.user_int.avg_delay_result.setVisible(False)
            self.user_int.label_5.setVisible(False)
            self.user_int.label_6.setVisible(False)
            self.user_int.fail_predict_lb.setText("Sorry unable to predict!\n "
                                                  "Please enter date within 15 days from today.")

    # Admin Page
    def authenticate(self):
        """
        This function checks if user is actually an admin and redirects to admin page
        if user is an admin.
        """
        password = self.user_int.password_input.text()
        # Password can be changed here.
        if password == "123":
            self.stacked_widget_pages.setCurrentIndex(2)
        else:
            self.user_int.error_msg_lb.setVisible(True)

    def handle_return_input(self):
        """
        This function obtains the start and end years entered by the admin.
        """
        years_input_info = self.user_int.years_input.text()
        self.process_input(years_input_info)
        return years_input_info

    def process_input(self, years_input_info):
        """
        This function processes whether the enters start and end years entered
        are in the correct format.
        :param years_input_info: the start and end years entered by the admin.
               Obtained by handle_return_input() function.
        """
        mes = "Please enter start & end year in correct format (no space) and press enter!"
        if "," in years_input_info:
            try:
                years = years_input_info.split(",")
                if len(years) == 2 and all(len(year) == 4 and year.isdigit() for year in years):
                    self.user_int.year_indicator.setVisible(True)
                    self.start_year, self.end_year = min(years), max(years)
                    self.user_int.year_indicator.setText("The start year is: "
                                                         + str(self.start_year)
                                                         + "\n" + "The end year is: "
                                                         + str(self.end_year))
                else:
                    self.user_int.year_indicator.setText(mes)
                    self.user_int.year_indicator.setVisible(True)

            except ValueError:
                self.user_int.year_indicator.setVisible(True)
                self.user_int.year_indicator.setText(mes)
        else:
            # Can't raise value error. Prompting admin to re-enter years in correct format.
            self.user_int.year_indicator.setVisible(True)
            self.user_int.year_indicator.setText(mes)

    def retrain_models(self, num_uploaded):
        """
        This function triggers models to be retrained after new files have been uploaded.
        """
        try:
            start_year_input = int(self.start_year)
            end_year_input = int(self.end_year)
        except TypeError:
            self.user_int.file_lb.setText("You have not entered a start or end year.")
        else:
            # Only triggers model combination if more than 2 files are uploaded
            if num_uploaded > 2:
                self.user_int.file_lb.setVisible(False)
                self.user_int.success_lb.setText("You have uploaded " +
                                                 str(num_uploaded) + " files.")
                # 1) Obtain entered start and end years entered by user.
                airports = pd.read_csv('resources/airport_codes.csv')

                # 2) Obtain historical weather data
                weather.get_historic_weather_data(airports, start_year=start_year_input,
                                                  end_year=end_year_input)
                # 3) Call data processing util

                data_processing.create_dataset(airport_path=AIRPORT_FOLDER_PATH,
                                               weather_path=WEATHER_FOLDER_PATH)
                # 4) Calls model training
                delay_predictor.create_model_from_dataset(
                    data_path="resources/generated/pickles/combined_flight_data")
                # 5) Print out new training and testing accuracies
                # For delay probability
                delay_probability_metrics = delay_predictor.get_classifier_metrics()
                delay_probability_metrics_results = ', '.join(str(item)
                                                              for item in
                                                              delay_probability_metrics[:-1])

                # For delay severity
                delay_severity_metrics = delay_predictor.get_regressor_metrics()
                delay_severity_metrics_results = ', '.join(str(item)
                                                           for item in delay_severity_metrics)
                self.user_int.new_mod_lb.setText("The model has been successfully trained!\n"
                                                 + "The training metrics for probability "
                                                   "of delay is \n"
                                                 + delay_probability_metrics_results + "\n"
                                                 + "The training metrics for severity "
                                                   "of delay is \n "
                                                 + delay_severity_metrics_results)
                self.user_int.new_mod_lb.setVisible(True)
                self.user_int.mod_title_lb.setVisible(True)
            else:
                print("Unable to retrain")

    def upload_files(self):
        """
        This function allows users to upload files and triggers data combination and modelling
        if files were uploaded.
        Type of files expected: zip-files containing .csv files for flight data.
        # Require admin to enter a start and end year before asking to upload data.
        For later: Print out training and testing accuracy, then ask
                if user would like to replace model.
                Asking if user would like to refit the model.
                self.user_int.retrain_optionlb.setText("Would you like to replace the model? ")
                self.user_int.retrain_optionlb.setVisible(True)
                self.user_int.option_btn.setVisible(True)
                self.user_int.option_btn.accepted.connect \
                   (lambda: self.user_int.refit_lb.setText("Replace model..."))
                 self.user_int.option_btn.rejected.connect \
                   (lambda: self.user_int.refit_lb.setText("Not replacing model."))
                Refit
                Can add a progress bar. When it hits 100% Display "Successfully retrained".
        """

        # Creates file upload dialog
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.ExistingFiles)
        files, _= self.file_dialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        num_uploaded = len(files)
        if not files:
            self.user_int.file_lb.setText("No files have been uploaded.")
            self.user_int.file_lb.setVisible(True)
            return
        if files:
            # Should only run model training if we uploaded multiple .zip containing .csv files.
            folder_path = "resources/flight_data"
            self.user_int.success_lb.setVisible(True)
            self.user_int.success_lb.setText("You have uploaded " + str(num_uploaded) + " file(s).")
            self.user_int.file_lb.setVisible(False)

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                print(file_path)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                except PermissionError:
                    print(f"Permission desnied: {file_path} ")
                except OSError as exception:
                    print(f"OS error while deleting {file_path}: {exception}")

            for file_path in files:
                file_name = os.path.basename(file_path)
                destination_path = os.path.join(folder_path, file_name)
                shutil.copy(file_path, destination_path)
            self.retrain_models(num_uploaded)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlightUi()
    window.show()
    sys.exit(app.exec_())
