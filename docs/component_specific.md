## BTS Flight Forecast

<b> Background </b>
BTS Flight Forecast is a tool to predict flight delays utilizing past weather data, and weather forecast, given a specified airport code, date, and time.
<b> Data source </b>
1. Flight Data: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr
2. Weather Data: https://www.wunderground.com/history

<b> Component 1: Graphical User Interface </b>

- Description: This component provides two interfaces
  1) Allow travelers to easily select their flight details (data,time,airport) to see delay predictions.
  2) Allow admins to login, upload historical flight data and trigger model retraining, and displays training and testing accuracies.
- Assumptions: Travellers possess necessary flight details and understand airport codes. Technicians are proficient in downloading data from BTS.

<b> Component 2: Weather Utility </b>
- Description: This component fetches both historical and forecasted weather data relevant to a user's chosen airport and timeframe. It uses APIs to retrieve historical data for a specific period and forecasted data for a specific airport and time.

<b> Component 3: Data Processor </b>
- Description: This component acts as a data cleaner and organizer. It takes historical flight and weather data, cleanses any inconsistencies, and combines them into a usable format for training the predictive model.

<b> Component 4: Delay Predictor </b>b>
- Description: It uses the processed data to train a machine learning model. Once trained, the model can predict the likelihood of flight delays based on the users input (date, time, airport).
