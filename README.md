![Build/Test Workflow](https://github.com/fangyulim/BTS_Flight_Forecast/actions/workflows/build_test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fangyulim/BTS_Flight_Forecast/badge.svg?branch=main)](https://coveralls.io/github/fangyulim/BTS_Flight_Forecast?branch=main)

<a id="introduction"></a>
## Introduction
Flight delays are a constant source of frustration for travelers, causing missed connections and disrupted schedules. Unpredictable weather and increasing air traffic make reliable information about potential delays even more critical. BTS Flight Forecast addresses this need by leveraging historical data and weather forecasts to empower travelers with delay predictions.

#### Team Members:
|            Name            |      GitHub       |
|:--------------------------:|:-----------------:|
| **Bruno Carvalho Barreto** |    *BrunoB42*     |
|      **Fang Yu Lim**       |    *fanguilim*    |
|    **Sushma Vankayala**    | *sushmavankayala* |

## Table of Contents
* [Introduction](#introduction)
* [Tasks of Interest](#tasks-of-interest)
* [Repository Structure](#repository-structure)
* [Installation](#installation)
    * [Environment](#environment)
    * [Data](#data)
    * [Application](#application)

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
│   ├── ComponentInteractionDiagramV2.pdf
│   ├── Milestone.md
│   ├── PseudoCode.md
│   ├── TechnologyReview.pdf
│   ├── README.md
│   ├── UseCases.md
│   ├── UserStories.pdf
├── flight_forecast/
│   ├── resources/
│   │   ├── flight_data/
│   │   │   ├── On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_2022_5.zip
│   │   │   ├── ...
│   │   │   ├── README.md
│   │   ├── generated/
│   │   │   ├── pickles
│   │   │   │   ├── combined_flight_data
│   │   │   │   ├── README.md
│   │   │   ├── weather_data
│   │   │   │   ├── BIL.csv
│   │   │   │   ├── BLI.csv
│   │   │   │   ├── ...
│   │   │   │   ├── TWF.csv
│   │   │   │   ├── README.md
│   │   │   ├── README.md
│   │   ├── README.md
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── tests_user_interface.py
│   │   ├── tests_weather.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_combination_1.py
│   │   ├── delay_modelling_2.py
│   │   ├── flight_delay_multi_page_ui.py
│   │   ├── weather.py
│   ├── README.md
├── POC/
│   ├── BTS_Demo_1_Data_Combination.ipynb 
│   ├── BTS_Demo_2_Delay_Prediction_Cleaning_And_Modelling.ipynb 
│   ├── BTS_Demo_3_Delay_Severity_Prediction_Cleaning_And_Modelling.ipynb 
│   ├── PyQT5_Demo.py
│   ├── PyQt5_GUI_Demo.ui
│   ├── README.md
├── .gitignore
├── environment.yml
├── LICENSE
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

To create our specified `BTS_Flight_Forecast` Conda environment, run the following command:
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
The raw data for our project is obtained from three different sources:
1. **Historical Flight Delays**: Data on past flight delays is obtained from the Bureau of Transportation Statistics (BTS) [https://www.transtats.bts.gov/Tables.asp?DB_ID=111]. 
2. **Weather Data**:
   - **Historic Weather Data**: Weather Underground's historical weather data API (https://api.weather.com/v1/location/KSEA:9:US/observations/historical.json) is used to gather historical weather information for various airport locations.
   - **Real-time Weather Forecasts**: The tool integrates with the Weather.com API (https://api.weather.com/v3/wx/forecast/hourly/15day) to access real-time and forecasted weather data for specific airport locations. 

[//]: # (TODO: Add Script for loading and training the data   )

<a id="application"></a>
### Application
A local application can be generated with the code:
```bash
conda activate BTS_Flight_Forecast
cd flight_forecast
python -m utils.flight_delay_multi_page_ui.py
```
This will pop up our tool's GUI.

[//]: # (TODO: Add examples folder and demo)