"""
This module constructs a two page user interface, links api calls and produce predictions.

The first page allows users to selection airport code, date, and if they want
a prediction of delay severity, or just delay prediction.

The second page allows admin to upload more data and retrain the model.
Comments: I ended up not putting state and airport name in option because
not all airports have a name.

To use this module, please use command: python -m utils.flight_delay_multi_page_ui in terminal.
To run using IDE, please change file paths.
"""
import csv
import sys
import pandas as pd
import os
import shutil

from datetime import datetime
from PyQt5 import uic   # , QtWidgets. This prevents errors
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListView, QComboBox, QAbstractItemView
#  QHBoxLayout, QWidget, QPushButton, QVBoxLayout, QStackedWidget, QLabel,
from PyQt5.QtCore import Qt, QDateTime, QTimeZone
from . import weather
from . import data_combination_1
from . import delay_modelling_2

# GUI file
QT_CREATOR_FILE = '../resources/flight_delay_multi_page.ui'
ui_main_window, QtBaseClass = uic.loadUiType(QT_CREATOR_FILE)


class Milestone2V2(QMainWindow):
    """
    This class initializes the GUI and the widgets.
    """

    def __init__(self):
        """
        function documentation: This function sets up the windows and actions for specific changes
        """
        # super(Milestone2V2, self).__init__()
        super().__init__()
        self.user_int = ui_main_window()
        self.user_int.setupUi(self)
        self.setup_ui()

        self.start_year = None
        self.end_year = None

        # Moves to admin login page when " Admin Login" button is clicked
        self.user_int.admin_login_btn.clicked.connect(
            lambda: self.stacked_widget_pages.setCurrentIndex(1))
        # Moves to main page when "Main Page" button is clicked
        self.user_int.main_page_btn.clicked.connect(
            lambda: self.stacked_widget_pages.setCurrentIndex(0))

        # Centering labels
        label_main_page = self.user_int.main_page_lb
        label_main_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label_login_page = self.user_int.login_page_lb
        label_login_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label_admin_page = self.user_int.admin_page_lb
        label_admin_page.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Instantiating widgets and functions used on main page.
        self.load_airport_list()
        self.load_airlines_list()

        # This will be used if we decide to move airport_selection as it's own function.
        # self.user_int.airport_selection.currentTextChanged.connect(self.airport_changed)
        self.user_int.PredictButton.clicked.connect(self.prediction)

        # Authentication page.
        self.user_int.error_msg_lb.setVisible(False)
        self.user_int.login_btn.clicked.connect(self.authenticate)

        # Upload page.
        self.user_int.years_input.returnPressed.connect(self.handle_return_input)
        self.user_int.file_lb.setVisible(False)
        self.user_int.upload_btn.clicked.connect(self.upload_files)
        self.user_int.new_mod_lb.setVisible(False)
        self.user_int.mod_title_lb.setVisible(False)
        self.user_int.option_btn.setVisible(False)
        self.user_int.retrain_optionlb.setVisible(False)
        self.user_int.refit_lb.setVisible(False)

    def setup_ui(self):
        """
        This function sets up the UI.
        - Sets up the dimension of the UI.
        - Instantiated stacked widget (pages).
        - Sets label/ widgets to not appear before user input.
        """
        width = 1200
        height = 750
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        # Instantiated stacked widget and set default page to be main page(user).
        self.stacked_widget_pages = self.user_int.stacked_widget
        self.stacked_widget_pages.setCurrentIndex(0)
        self.user_int.avg_delay_result.setVisible(False)
        self.user_int.label_6.setVisible(False)
        self.user_int.prob_delay_result.setVisible(False)
        self.user_int.label_5.setVisible(False)
        self.user_int.fail_predict_lb.setVisible(False)

    def load_airport_list(self):
        """
        This function displays the list of airports in the dropdown bar.
        Currently, we are only using the list of airports in the pacific northwest.
        """
        # Couldn't figure out path.
        with open("../resources/airport_codes.csv", "r", encoding="utf-8") as file:
            next(file)  # skips the header.
            airport_codes = [row[0] for row in csv.reader(file)]

        # Clear the existing items in airport_selection widget
        self.user_int.airport_selection.clear()
        # Adding airport names to the widget.
        self.user_int.airport_selection.addItems(airport_codes)

    def load_airlines_list(self):
        with open("../resources/airline_list.csv", "r", encoding="utf-8") as file:

            next(file)  # skips the header.
            airline_list = [row[0] for row in csv.reader(file)]

        self.user_int.airline_selection.clear()
        self.user_int.airline_selection.addItems(airline_list)

    def prediction(self):
        """
        This function processes input information and displays prediction
        """
        airport_selected = self.user_int.airport_selection.currentText()
        airline_selected = self.user_int.airline_selection.currentText()

        date_selection = self.user_int.date_selection.date().toString("yy.MM.dd")
        time_selection = self.user_int.time_selection.time().toString("HH:mm:ss")

        date = self.user_int.date_selection.date()
        time = self.user_int.time_selection.time()
        gmt_timezone = QTimeZone.utc()
        date_time_selection = QDateTime(date,time, gmt_timezone)
        unix_timestamp = date_time_selection.toSecsSinceEpoch()

        # If selected day is within 15 days, then we are able to give a prediction
        current_date = datetime.now()
        qdate = self.user_int.date_selection.date()
        date_selected = datetime(qdate.year(), qdate.month(), qdate.day())
        difference = abs(current_date - date_selected)
        month_input = date.month()

        day_input = date.day()
        year_input = date.year()
        if 1 < difference.days < 15:
            # TODO:
            # 1. call the get_weather_forecast from weather.py (airport code, timestamp in seconds): check
            # 2. pass the output from step1 to predict_delay_probability from data_modelling_2.py
            # call the predict_delay_time from data_modelling_2.py if the checkbox is selected
            RELEVANT_USER_INPUT_COLUMNS = ['Year', 'Month', 'DayofMonth','Origin']
            user_input = [year_input, month_input, day_input,airport_selected]

            forecast_weather_df = weather.get_weather_forecast(airport_selected,unix_timestamp)
            forecast_weather_df_focused = forecast_weather_df[['temp', 'dewPt', 'day_ind',
                                                               'rh', 'wdir_cardinal', 'gust', 'wspd', 'pressure', 'wx_phrase']]
            FORECAST_WEATHER_COLUMNS = list(forecast_weather_df_focused.columns)
            forecast_weather_df_focused_values = forecast_weather_df_focused.values.tolist()[0]

            combined_df = pd.DataFrame(columns=RELEVANT_USER_INPUT_COLUMNS + FORECAST_WEATHER_COLUMNS )
            combined_df.loc[0,:] = user_input+forecast_weather_df_focused_values

            # print(combined_df)

            if self.user_int.check_box.isChecked():

                severity_probability = delay_modelling_2.predict_delay_severity(combined_df)
                # severity_prediction = airport_selected + date_selection + time_selection \
                #                      + "severity prediction is"
                print("severity probability")
                print(severity_probability)
                severity_prediction = "The results are"
                self.user_int.avg_delay_result.setText(severity_prediction)
                self.user_int.avg_delay_result.setVisible(True)
                self.user_int.label_6.setVisible(True)

            else:
                self.user_int.avg_delay_result.setVisible(False)
                self.user_int.label_6.setVisible(False)

            delay_probability = delay_modelling_2.predict_delay_probability(combined_df)
            print("delay")
            print(delay_probability)
            delay_prediction = airport_selected + date_selection + time_selection
            self.user_int.prob_delay_result.setVisible(True)
            self.user_int.label_5.setVisible(True)
            self.user_int.fail_predict_lb.setVisible(False)
            self.user_int.prob_delay_result.setText("The predicted delay is")
        else:
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
        if password == "pw123":
            self.stacked_widget_pages.setCurrentIndex(2)
        else:
            self.user_int.error_msg_lb.setVisible(True)

    def handle_return_input(self):
        years_input_info = self.user_int.years_input.text()
        self.process_input(years_input_info)

        # Define a method to process the input
    def process_input(self, years_input_info):
        if "," in years_input_info:
            years = years_input_info.split(",")
            if len(years) == 2 and all(len(year) == 4 and year.isdigit() for year in years):
                self.start_year, self.end_year = min(years), max(years)
                print("The start_year is", self.start_year)
                print("The end year is", self.end_year)
            else:
                print("Please enter start and end year in format YYYY,YYYY with no space.")
        else:
            print("Please enter start and end year in format YYYY,YYYY with no space.")

    def upload_files(self):
        """
        This function allows users to upload files and triggers pipeline
        for data cleaning and model retraining.
        """

        # Creates file upload dialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        # Open the file dialog and get the selected file paths
        files, _ = file_dialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        # Returns the number of files uploaded, and saves the files in 'flight_data' folder.

        if files:
            # Should only run model training if we uploaded multiple .zip containing .csv files.
            folder_path ="./flight_data"
            num_uploaded = len(files)
            self.user_int.file_lb.setText("You have uploaded " + str(num_uploaded) + " file(s).")
            self.user_int.file_lb.setVisible(True)
            for file_path in files:
                file_name = os.path.basename(file_path)
                destination_path = os.path.join(folder_path,file_name)
                shutil.move(file_path, destination_path)

            # Call data collection + cleaning pipeline
            # 1) Call weather API to obtain historic weather data

            airports = pd.read_csv('../resources/airport_codes.csv')
            start_year_input = self.start_year
            end_year_input = self.end_year
            # weather.get_historic_weather_data(airports, start_year_input, end_year_input)

            # 2) Create dataset:
            # create_dataset(airport_path="./flight_data", weather_path="./weather_data")

            # 3) Call model retrain:
            # create_model_from_dataset(data_path="combined_flight_data")

            # 4) Prints out new training and testing accuracy
            # For delay probability
            # get_classifier_metrics()
            # For delay severity
            # get_regressor_metrics()
            self.user_int.new_mod_lb.setText("The new model training accuracy is 0.478922. \n "
                                             "The new model testing accuracy is 0.4629312. \n"
                                             "The model has been replaced!")
            self.user_int.new_mod_lb.setVisible(True)
            self.user_int.mod_title_lb.setVisible(True)

            # For later: Print out training and testing accuracy, then ask
            # if user would like to replace model.
            # Asking if user would like to refit the model.
            # self.user_int.retrain_optionlb.setText("Would you like to replace the model? ")
            # self.user_int.retrain_optionlb.setVisible(True)
            #self.user_int.option_btn.setVisible(True)
            # self.user_int.option_btn.accepted.connect \
            #    (lambda: self.user_int.refit_lb.setText("Replace model..."))
            #self.user_int.option_btn.rejected.connect \
            #    (lambda: self.user_int.refit_lb.setText("Not replacing model."))
            # Refit
            # Can add a progress bar. When it hits 100% Display "Successfully retrained".

        else:
            self.user_int.file_lb.setText("No files have been uploaded.")
            self.user_int.file_lb.setVisible(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Milestone2V2()
    window.show()
    sys.exit(app.exec_())
