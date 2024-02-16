### Component 1: User GUI

Creating GUI elements within window class

```python
import PyQT6

layout = box_layout()

airport_input_prompt = label("Enter airport code")
airport_input = line_edit()
airport_input.when_changed.call_function(update_airport)
layout.add(airport_input_prompt)
layout.add(airport_input)

time_input_prompt = label("Enter flight date and time")
time_input = line_edit()
airport_input.when_changed.call_function(update_date_and_time)
layout.add(time_input_prompt)
layout.add(time_input)

weather_input_prompt = label("Select weather")
weather_input = drop_down_combo_box()
airport_input.when_changed.call_function(update_weather)
layout.add(weather_input_prompt)
layout.add(weather_input)

## add more components if modelling results deem them to be important

predict_button = button()
predict_button.when_pushed.call_function(run_model)
layout.add(predict_button)

self.predict_result = label()
layout.add(predict_result)

widget = Widget()
widget.set_layout(layout)
```

Defining GUI element functions

```python
def update_airport(self, updated_airport):
    self.airport_code = updated_airport

def update_date_and_time(self, updated_datetime):
    self.datetime = updated_datetime

def update_weather(self, updated_weather):
    self.weather = updated_weather

def run_model(self):
    model = unpickle("file_path_to_model")
    result = model.predict([self.airport_code,
                            self.datetime,
                            self.weather])
    self.predict_result.text = result
```

### Component 2: Flight Delay Model

Unpacking processed data

```python
X_train_processed, X_test_processed, y_train, y_test = unpickle(data_file_paths)
```
Fitting and evaluating model

Note: Final component will only include best performing model

```python
for current_model in list_of_models_being_considered:
    model_with_parameter_sweep = grid_search(current_model())
    model_with_parameter_sweep.fit(X_train_processed, y_train)
    model_performance = model_with_parameter_sweep.score(X_test_processed, y_test)
    plot(model_performance)

pickle(best_model)
```

### Component 3: Admin Model Updating GUI

Creating GUI elements within window class

```python
import PyQT6

layout = box_layout()

airline_data_input_prompt = label("Upload airline data from the BTS")
airline_data_input = user_upload()
airport_data_input.when_uploaded.call_function(update_BTS_data)
layout.add(airport_input_prompt)
layout.add(airport_input)

hyperparam_input_prompt = label("Upload airline data from the BTS")
hyperparam_input = line_edit()
hyperparam_input.when_changed.call_function(update_hyperparams)
layout.add(hyperparam_input_prompt)
layout.add(hyperparam_input)

train_button = button()
train_button.when_pushed.call_function(run_component_6)
layout.add(train_button)

self.test_results = label()
layout.add(test_results)

save_button = button()
save_button.when_pushed.call_function(save_model)
layout.add(save_button)

widget = Widget()
widget.set_layout(layout)
```

Defining GUI element functions

```python
def update_BTS_data(self, updated_data):
    self.BTS_data = updated_data

def update_hyperparams(self, updated_hyperparams):
    self.hyperparams = updated_hyperparams

def run_component_6(self):
    model, score = run_model_update_script(self.BTS_data, self.hyperparams)
    self.test_results.text = report(score)
    self.current_model = model

def save_model(self):
    pickle(self.current_model)
```

### Component 4: Weather Data API Caller

Will be called by Component 6

```python
airport_codes = airline_data.origin_codes.unique()
# Looping over airport codes in BTS data
for airport in airport_codes:
    weather_data = call_weather_api(airport_code, query_params)
    # Assigning weather from weather data to each flight time
    for flight_index in airline_data[airline_data.origin_code == airport].index:
        time_of_interest = gest_date_and_time(airline_data[flight_index])
        airline_data[flight_index, "weather"] = get_closest_entry(weather_data, time_of_interest)
# Returning airline data with added weather column(s)
return airline_data
```

### Component 5: Data Pre-processing Steps

Obtaining data and separating into target/predictors

```python
df = unpickle("flight_data_path")
target_df, predictor_df = separate(df)
relevant_columns = ["..","..."]
predictor_df = predictor_df[ relevant_columns ]
```

Looping over data for first-time-only EDA

(Not included in final component)

```python
for column in relevant_columns:
    bar_plot(sort(predictor_df.column))
    histogram(predictor.columns)
```

Cleaning and splitting data

```python
cleaning_transformer = nan_outlier_and_new column_cleaner()
predictor_df = cleaning_transformer(predictor_df)
target_df = target_df.iloc[ predictor_df.index ]
X_train, X_test, y_train, y_test = train_test_split(predictor_df, target_df)

scaler = standard_scaler()
encoder = one_hot_encoder()
X_train_processed = combine(scaler(get_numeric_columns(X_train)), encoder(get_categorical_columns(X_train)))
X_train_processed = combine(scaler(get_numeric_columns(X_test)), encoder(get_categorical_columns(X_test)))
pickle(X_train_processed, X_test_processed, y_train, y_test)
```

### Component 6: Model Update Script

Creating pipeline object

Will only be performed once

```python
update_pipeline = sklearn.Pipeline()
update_pipeline.add(cleaning_step, cleaning_transformer)
update_pipeline.add(scaling_step, scaler)
update_pipeline.add(encoding_step, encoder)
update_pipeline.add(modelling_step, model_with_parameter_sweep)
```

Getting user data

```python
airline_data = getBTSDataFromGUI(component_3)
airline_data_with_weather = getWeatherDataAPI(component_4, airline_data)
```

Parameter sweeping and retraining model

```python
model, score = update_pipeline.fit(airline_data_with_weather, hyperparameters)
return (model, score)

does_user_approve_of_current_model = askUser()
if does_user_approve_of_current_model:
    pickle(model)
```