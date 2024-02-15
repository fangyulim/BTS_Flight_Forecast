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

Note: Component 4 will only include best performing model

```python
for current_model in list_of_models_being_considered:
    model_with_parameter_sweep = grid_search(current_model())
    model_with_parameter_sweep.fit(X_train_processed, y_train)
    model_performance = model_with_parameter_sweep.score(X_test_processed, y_test)
    plot(model_performance)

pickle(best_model)
```

### Component 3: Data Pre-processing Steps

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

### Component 4: Model Update Script

Creating pipeline object

```python
update_pipeline = sklearn.Pipeline()
update_pipeline.add(cleaning_step, cleaning_transformer)
update_pipeline.add(scaling_step, scaler)
update_pipeline.add(encoding_step, encoder)
update_pipeline.add(modelling_step, model_with_parameter_sweep)
```

Getting user data

```python
weather_data = promptUserForWeatherData()
airline_data = promptUserForBTSData()
combined_data = join_on_airline_code(weather_data, airline_data)
```

Parameter sweeping and retraining model

```python
model, score = update_pipeline.fit(combined_data, hyperparameters)
report_score(score)
does_user_approve_of_current_model = askUser()
if does_user_approve_of_current_model:
    pickle(model)
```