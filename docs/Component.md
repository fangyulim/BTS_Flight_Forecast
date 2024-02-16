## Use Case 1: View Flight Delay Prediction

### Component 1: User GUI

- <b>Description:</b> Provides a user interface for inputting flight details and displaying the predicted flight delay probability.
- <b>Output:</b> Display of flight delay probability.
- <b>Assumptions:</b> Users possess necessary flight details and understand airport codes.

### Component 2: Predictive Model

- <b>Description:</b> Orchestrates the retrieval of the prediction model and executes predictions.
- <b>Inputs:</b> Airport code, departure date and time
- <b>Output:</b> Probability of flight delay.
- <b>Assumptions:</b> A trained ML prediction model is available.

## Use Case 2: Train/Re-train Prediction Model

### Component 3: Admin GUI

- <b>Description:</b> Interface for technicians to upload flight data, trigger model training/re-training, and finetune parameters.
- <b>Output:</b> Status display indicating success or failure of upload/retrain operations.
- <b>Assumptions:</b> Technicians are proficient in downloading data from BTS.

### Component 4: Weather Data Collection Pipeline

- <b>Description:</b> Fetches historic weather data between two dates
- <b>Inputs:</b> Start date, End date
- <b>Output:</b> Cleaned and processed Weather Data between given dates
- <b>Assumptions:</b> The input dates are in the past. The weather APIs are up and running.

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