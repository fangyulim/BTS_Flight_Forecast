## BTS Flight Forecast
<b> Background </b>b>
BTS Flight Forecast is a tool to predict flight delays utilizing past weather data, and weather forecast, given a specified airport code, date, and time.
<b> Data source </b>
1. Flight Data: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr
2. Weather Data: https://www.wunderground.com/history

### Use Case 1: View Flight Delay Prediction

<b> Component 1: User GUI </b>

- Description:Provides a user interface for inputting flight details and displaying the predicted flight delay probability.
- Output: Display of flight delay probability.
- Assumptions: Users possess necessary flight details and understand airport codes.

<b>Component 2: Predictive Model </b>

- Description: Orchestrates the retrieval of the prediction model and executes predictions.
- Inputs: Airport code, departure date and time
- Output: Probability of flight delay.
- Assumptions: A trained ML prediction model is available.

### Use Case 2: Train/Re-train Prediction Model

<b>Component 3: Admin GUI</b>

- Description: Interface for technicians to upload flight data, trigger model training/re-training, and finetune parameters.
- Output: Status display indicating success or failure of upload/retrain operations.
- Assumptions: Technicians are proficient in downloading data from BTS.

<b> Component 4: Weather Data Collection Pipeline </b>

- Description: Fetches historic weather data between two dates
- Inputs: Start date, End date
- Output: Cleaned and processed Weather Data between given dates
- Assumptions: The input dates are in the past. The weather APIs are up and running.

### Component 5: Data Processing Pipeline

- <b>Description:</b> Manages the processing of uploaded flight data. Merges the flight schedules with corresponding weather data.
- <b>Inputs:</b> Existing merged data, uploaded data on flight schedules, weather data collected by Weather Data Collection pipeline.
- <b>Output:</b> Cleaned and merged dataset containing flight schedules and corresponding weather parameters.
- <b>Assumptions:</b> Uploaded data conforms to expected schema.

### Component 6: Model Trainer

- <b>Description:</b> Initiates model training based on provided data, evaluates model accuracy.
- <b>Inputs:</b> Existing model, training/testing data.
- <b>Output:</b> Training/testing accuracy.
- <b>Assumptions:</b> Training and testing data format aligns with model requirements.