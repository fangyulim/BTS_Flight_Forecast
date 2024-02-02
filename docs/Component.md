### Usecase 1: View Flight Delay Prediction
Component 1:
- GUI (Allows user input, and output of flight delay predictions)
- Inputs: 
  None
- Output: 
  Display of the output from the prediction model, providing flight delay probability. 
- Assumptions
  Users know the airport code, and flight details. 

Component 2:
- Control logic (fetches the prediction model)
- Inputs:
  Airport code, string of alphanumeric that will be selected from a dropdown bar.
  date and time, datetime that will be selected from a dropdown bar.
  Model: ML prediction model trained on historic data, for flight delay probability.
- Outputs:
  Probability of delay, float.
Assumptions: The model is already trained.
  
  
### Usecase 2: Loading new data and re-training model
Component 1:
- GUI (Allows technician to upload data, and re-train the model and make modifications if necessary)
- Outputs: 
  Display of upload/ retrain status. (Fail/Success)
- Assumptions:
  The technician knows how to download the data from BTS.
  
Component 2:
- Data processor (Pipeline that uses the uploaded data, fetches the corresponding weather data, and merges with previous data,involves data cleaning and data wrangling.)
- Input:
  Uploaded data
  Existing data 
- Output:
  Cleaned and merged data
- Assumption:
  Uploaded data has the required columns to be transformed to existing schema.
  
Component 3:
- Model trainer (Triggers a model training based on the provided data. Trains the model on the initial or updated data. Provides testing accuracy.)
- Input:
  Existing model
  Training/ Testing data
- Output:  
  Training/testing accuracy
- Assumptions:
  Training and testing data are in the format as expected by the model.
  