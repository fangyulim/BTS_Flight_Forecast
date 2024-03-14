![Build/Test Workflow](https://github.com/fangyulim/BTS_Flight_Forecast/actions/workflows/build_test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fangyulim/BTS_Flight_Forecast/badge.svg?branch=main)](https://coveralls.io/github/fangyulim/BTS_Flight_Forecast?branch=main)

<a id="introduction"></a>
## Introduction
Flight delays are a constant source of frustration for travelers, causing missed connections and disrupted schedules. Unpredictable weather and increasing air traffic make reliable information about potential delays even more critical. BTS Flight Forecast addresses this need by leveraging historical data and weather forecasts to empower travelers with delay predictions.

#### Team Members:
|            Name            |      GitHub       |
|:--------------------------:|:-----------------:|
| **Bruno Carvalho Barreto** |    *BrunoB42*     |
|      **Fang Yu Lim**       |    *fangyulim*     |
|    **Sushma Vankayala**    | *sushmavankayala* |

## Table of Contents
* [Introduction](#introduction)
* [Tasks of Interest](#tasks-of-interest)
* [Repository Structure](#repository-structure)
* [Installation](#installation)
    * [Environment](#environment)
    * [Data](#data)
    * [Predictive Model](#predictive_model)
    * [Application](#application)
    * [Testing](#testing)
    * [Customizations](#customizations)

[//]: # (* [Examples]&#40;#examples&#41;)

<a id="tasks-of-interest"></a>
## Tasks of Interest
- **Flight Delay Prediction**:
    - Develop a user interface allowing travelers to enter a departure airport code, date, and time.
    - Utilize the prediction model to estimate the likelihood of a flight delay for the specified departure.
    - Clearly display the predicted delay probability to the user.
- **Model Retraining (Admin Only)**:
    - Implement a secure interface for authorized users to upload new flight data.
    - Validate the uploaded data format to ensure compatibility with the model.
    - Integrate a functionality to retrain the prediction model using the uploaded data, improving its accuracy over time.
    - Provide feedback to the admin user on the success or failure of the retraining process.
  
<a id="repository-structure"></a>
## Repository Structure
Here is an overview of our project structure:
```

├── docs/
│   ├── Background.md
│   ├── Component.md
│   ├── Component_Diagram.png
│   ├── ComponentInteractionDiagramV2.pdf
│   ├── Interaction_Diagram_1.png
│   ├── Interaction_Diagram_2.png
│   ├── Milestone.md
│   ├── PseudoCode.md
│   ├── TechnologyReview.pdf
│   ├── UseCases.md
│   ├── UserStories.pdf
├── examples/
│   ├── 1_Landing page - User.png
│   ├── 2_Date and Time selection.png
│   ├── 3_Delay Prediction.png
│   ├── 4_Delay Severity Prediction.png
│   ├── 5_Admin Login.png
│   ├── 6_Admin Landing Page.png
│   ├── 7_Model Training Response.png
├── BTS_Flight_Forecast/
│   ├── resources/
│   │   ├── flight_data/
│   │   │   ├── On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_2022_5.zip
│   │   │   ├── ...
│   │   ├── generated/
│   │   │   ├── pickles/
│   │   │   │   ├── combined_flight_data
│   │   │   ├── weather_data/
│   │   │   │   ├── BIL.csv
│   │   │   │   ├── BLI.csv
│   │   │   │   ├── ...
│   │   │   │   ├── TWF.csv
│   │   ├── testing_resources/
│   │   │   ├── invalid_name_weather_data/
│   │   │   ├── test_airport_data/
│   │   │   ├── test_weather_data/
│   │   │   ├── encoder.pkl
│   │   │   ├── test_date_df.csv
│   │   │   ├── weather_test.csv
│   │   ├── airport_codes.csv
│   │   ├── flight_delay_multi_page.ui
│   │   ├── README.md
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_user_interface.py
│   │   ├── test_weather.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_processing.py
│   │   ├── delay_predictor.py
│   │   ├── flight_delay_multi_page_ui.py
│   │   ├── weather.py
├── .gitignore
├── environment.yml
├── LICENSE
├── pylintrc
├── pyproject.toml
├── README.md (Current File)
├── requirements.txt
```

<a id="installation"></a>
## Installation

This repository can be cloned locally by running the following `git` command:
```bash
git clone https://github.com/fangyulim/BTS_Flight_Forecast.git
```
Please note that Git is required to run the above command. For instructions on downloading Git, please see [the GitHub guide](https://github.com/git-guides/install-git).

<a id="environment"></a>
### Environment
This application is built on top of multiple Python packages with specific version requirements. Installing these packages can cause conflicts with other packages in the workspace. As a work-around, we recommend to use `conda` to create an isolated Python environment with all necessary packages. Specifically, the list of necessary packages can be found at in the [`environment.yml`](./environment.yml) file.

To create our specified `BTS_Flight_Forecast` Conda environment, run the following command from the folder containing environment.yml
```bash
conda env create -f environment.yml
```

Once the Conda environment is created, it can be activated by:
```bash
conda activate BTS_Flight_Forecast
```
After coding inside the environment, it can be deactivated with the command:
```bash
conda deactivate
```

Please note that Conda must be installed for the above commands to work. For instructions on installing Conda, please visit [Conda.io](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

<a id="data"></a>
### Data
For this project, we use has a static list of airports in the Pacific Northwest. This information is stored in the resources folder as airport_codes.csv
The raw data for our project is obtained from three different sources:
1. **Historical Flight Delays**: Data on past flight delays is obtained from the Bureau of Transportation Statistics (BTS) [https://www.transtats.bts.gov/Tables.asp?DB_ID=111]. 
2. **Weather Data**:
   - **Historic Weather Data**: Weather Underground's historical weather data API (https://api.weather.com/v1/location/KSEA:9:US/observations/historical.json) is used to gather historical weather information for various airport locations.
   - **Real-time Weather Forecasts**: The tool integrates with the Weather.com API (https://api.weather.com/v3/wx/forecast/hourly/15day) to access real-time and forecasted weather data for specific airport locations. 

<a id="predictive_model"></a>
### Predictive Model
Predictive models pretrained on historic data of 33 airports from 2022-2023 are stored in the resources folder as pickles. The tool uses these models to predict the probability and severity of delays.

<a id="application"></a>
### Application
A local application can be generated by running the below code from the folder 'BTS_Flight_Forecast'
```bash
conda activate BTS_Flight_Forecast
python -m utils.flight_delay_multi_page_ui
conda deactivate BTS_Flight_Forecast
```
This will pop up our tool's GUI.

<a id="testing"></a>
### Running Tests
For running the tests, execute the following commands from the folder 'BTS_Flight_Forecast'
```bash
# enable offscreen setting for the GUI
export QT_QPA_PLATFORM=offscreen
python -m unittest discover
# disable offscreen setting for the GUI. This command MUST to be executed for the GUI to popup for further usage.
export QT_QPA_PLATFORM=
```
<a id="customizations"></a>
### Customizations (optional)
The current model is trained on historic flight and weather data corresponding to Pacific North West airports over the years 2022 - 2023.

1. **Extending to other airports**: The airport_codes.csv list needs to be updated to include information about new airport codes. If any airport has multiple airport codes, please use the code compatible with Weather Underground APIs.
2. **Extending to other years**: Years of interest can be provided as input in the UI or as arguments to the script.

You can download data and retrain the model in the 2 ways listed below. Please note that this step involves fetching the historic data for all airports listed in the airports_cv over the given range of years.
Note: For 2 year worth of data corresponding to 33 airports in the airport_codes.csv, this step (data collection, data processing and model training) takes about 1 hour.

1. **Using tool's GUI**:
    - Download data from BTS.
    - Use the admin page in the tool to upload the flight data.
    - Provide start and end years of the data.
    - Click retrain.
2. **Using script**:Update the START_YEAR and END_YEAR values in BTS_Flight_Forecast/scripts/reset_and_setup.py. Run the below script from the folder 'BTS_Flight_Forecast'.
   ```bash
    conda activate BTS_Flight_Forecast
    python -m scripts.reset_and_setup
    conda deactivate
    ```