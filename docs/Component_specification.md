##  Background 

BTS Flight Forecast is a tool to predict flight delays utilizing past weather data, and weather forecast, given a specified airport code, date, and time.

## Data sources

1. Flight Delays: Historical flight delay information is obtained from the Bureau of Transportation Statistics (BTS) https://www.transtats.bts.gov/Tables.asp?DB_ID=111.
2. Weather Data: The tool incorporates weather data using WeatherWunder APIs. These return the weather corresponding to an airport code.
   - Historical Weather: https://api.weather.com/v1/location/KSEA:9:US/observations/historical.json
   - Real-time Weather Forecasts: https://api.weather.com/v3/wx/forecast/hourly/15day

### Component: Graphical User Interface
#### User Screen
- <b>Description:</b> Provides a user interface for inputting flight details and displaying the predicted flight delay probability.
- <b>Output:</b> Display of flight delay probability.
- <b>Assumptions:</b> Users possess necessary flight details and understand airport codes.

#### Admin Screen
- <b>Description:</b> Interface for technicians to upload flight data, trigger model training/re-training, and finetune parameters.
- <b>Output:</b> Status display indicating success or failure of upload/retrain operations.
- <b>Assumptions:</b> Technicians are proficient in downloading data from BTS.

### Component: Delay Predictor

- <b>Description:</b> Orchestrates the retrieval of the prediction model and executes predictions.
- <b>Inputs:</b> Airport code, departure date and time
- <b>Output:</b> Probability of flight delay.
- <b>Assumptions:</b> A trained ML prediction model is available.

### Component: Weather Utility

- <b>Description:</b> Fetches historic weather data between two dates
- <b>Inputs:</b> Start date, End date, Airport Code
- <b>Output:</b> Cleaned and processed Weather Data between given dates
- <b>Assumptions:</b> The input dates are in the past. Airport Code is valid. The weather APIs are up and running.

### Component: Data Processing

- <b>Description:</b> Manages the processing of uploaded flight data. Merges the flight schedules with corresponding weather data.
- <b>Inputs:</b> Existing merged data, uploaded data on flight schedules, weather data collected by Weather Data Collection pipeline.
- <b>Output:</b> Cleaned and merged dataset containing flight schedules and corresponding weather parameters.
- <b>Assumptions:</b> Uploaded data conforms to expected schema.