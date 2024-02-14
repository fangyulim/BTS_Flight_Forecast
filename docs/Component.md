## Use Case 1: View Flight Delay Prediction

### Component 1: GUI

- <b>Description:</b> Provides a user interface for inputting flight details and displaying the predicted flight delay probability.
- <b>Output:</b> Display of flight delay probability.
- <b>Assumptions:</b> Users possess necessary flight details and understand airport codes.

### Component 2: Predictive Model Controller

- <b>Description:</b> Orchestrates the retrieval of the prediction model and executes predictions.
- <b>Inputs:</b> Airport code, departure date and time, weather conditions.
- <b>Output:</b> Probability of flight delay.
- <b>Assumptions:</b> A trained ML prediction model is available.

## Use Case 2: Loading New Data and Re-training Model

### Component 1: Data Management GUI

- <b>Description:</b> Interface for technicians to upload data, trigger model re-training, and handle modifications.
- <b>Output:</b> Status display indicating success or failure of upload/retrain operations.
- <b>Assumptions:</b> Technicians are proficient in downloading data from BTS.

### Component 2: Data Processing Pipeline

- <b>Description:</b> Manages the processing of uploaded data, including merging with existing data, data cleaning, and transformation.
- <b>Inputs:</b> Uploaded data, existing data.
- <b>Output:</b> Cleaned and merged dataset.
- <b>Assumptions:</b> Uploaded data conforms to expected schema.

### Component 3: Model Trainer

- <b>Description:</b> Initiates model training based on provided data, evaluates model accuracy.
- <b>Inputs:</b> Existing model, training/testing data.
- <b>Output:</b> Training/testing accuracy.
- <b>Assumptions:</b> Training and testing data format aligns with model requirements.