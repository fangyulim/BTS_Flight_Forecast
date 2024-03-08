'''
This module trains two models of flight delay in the USA.

In this module, a dataset of airport flight and weather data is preprocessed into numeric sparse
matrices and used to traing a classifier model that predicts if a flight will be delayed and a
regression model that predicts the severity of flight delays. For both of these models, functions
are defined that allow for a preiction to be made or for model training statistics to be reported.
'''

import pickle

import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression, LinearRegression


TARGET_COL_CLASSIFIER = "ArrDel15"
TARGET_COL_REGRESSOR = "ArrDelayMinutes"

# RELEVANT_COLS = ('Year', 'Quarter', 'Month', 'DayofMonth', 'DayOfWeek', 'Distance',
#                  'Origin', 'Dest', 'Reporting_Airline', 'temp', 'dewPt', 'day_ind',
#                  'rh', 'wdir_cardinal', 'gust', 'wspd', 'pressure', 'wx_phrase')

RELEVANT_COLS = ['Year', 'Month', 'DayofMonth','Origin','temp', 'dewPt', 'day_ind',
                 'rh', 'wdir_cardinal', 'gust', 'wspd', 'pressure', 'wx_phrase']

def pre_process_dataset(df_to_process, \
                        target_col=TARGET_COL_CLASSIFIER, \
                        relevant_columns = RELEVANT_COLS):
    '''
    Preprocesses flight data for use in training an sklearn model.

    This function takes in a Pandas DtaFrame of flight and weather data and pre-processes it by
    by splitting the data into train/test pairs and into target/predictor datasets. The split
    data is then prepared for training by scaling numeric data onto a mean of 0 and variance
    of 1 and by one-hot encoding categorical variables into simple numeric data columns.

    Parameters
    ----------
    df_to_process: A Pandas dataframe containing the data to be pre-processed.
    target_col: The columns that will be the prediction target of the future model
    relevant_columns: The columns that will be used to predict the target

    Returns
    -------
    A tuple containing, in order:
    * a scipy sparse matrix with training predictor data
    * a Pandas Series with training target data
    * a scipy sparse matrix with testing predictor data
    * a Pandas Series with testing target data
    '''
    target_series = df_to_process[[target_col]]
    input_df = df_to_process.drop(target_col,axis=1)
    input_df = input_df[relevant_columns]

    x_train, x_test, y_train, y_test = train_test_split(input_df, target_series)

    numeric_cols = x_train.dtypes[(x_train.dtypes == 'int64') | \
                                  (x_train.dtypes == 'float64')].index.tolist()
    non_numeric_cols = x_train.dtypes[(x_train.dtypes != 'int64') & \
                                      (x_train.dtypes != 'float64')].index.tolist()

    encoder = ColumnTransformer([
    ('scaler', StandardScaler(), numeric_cols),
    ('one_hot', OneHotEncoder(drop='first', handle_unknown='ignore'), non_numeric_cols)],
    remainder='passthrough',
    verbose_feature_names_out=False)

    x_train.columns = x_train.columns.astype(str)
    x_test.columns = x_test.columns.astype(str)
    encoder.fit(x_train)
    x_train_sparse = encoder.transform(x_train)
    #x_train_columns = encoder.get_feature_names_out()
    x_test_sparse = encoder.transform(x_test)
    #x_test_columns = encoder.get_feature_names_out()
    with open('encoder.pkl','wb') as file:
        pickle.dump(encoder,file)

    return (x_train_sparse, y_train,
            x_test_sparse, y_test,)


def train_classifier(datasets):
    '''
    Trains a logistic regression classifier for flight delay probability.

    Parameters
    ----------
    datasets: a tuple containing, in order:
    * a scipy sparse matrix with training predictor data
    * a Pandas Series with training target data
    * a scipy sparse matrix with testing predictor data
    * a Pandas Series with testing target data

    Returns
    -------
    A tuple containing, in order:
    * A logistic regression model object
    * The training score of the model
    * The testing score of the model
    '''
    # Defining logistic regression parameters to sweep over
    logreg_params = {
        'penalty':['l1','l2'],
        'C':[0.1,1,10]
    }
    # GridSearching logistic regression classifiers
    logreg_grid = GridSearchCV(LogisticRegression(solver='liblinear'), logreg_params, n_jobs=-2)
    logreg_grid.fit(datasets[0], np.ravel(datasets[1]))
    # Printing out train and test accuracy scores
    train_acc = logreg_grid.score(datasets[0], datasets[1])
    test_acc = logreg_grid.score(datasets[2], datasets[3])
    # Generating confusion matrix
    conf_matrix = ConfusionMatrixDisplay.from_estimator(logreg_grid, \
                                                        datasets[2], \
                                                        datasets[3], \
                                                        cmap='magma')
    return (logreg_grid, train_acc, test_acc, conf_matrix)


def train_regressor(datasets):
    '''
    Trains a linear regressor for flight delay severity.

    Parameters
    ----------
    datasets: a tuple containing, in order:
    * a scipy sparse matrix with training predictor data
    * a Pandas Series with training target data
    * a scipy sparse matrix with testing predictor data
    * a Pandas Series with testing target data

    Returns
    -------
    A tuple containing, in order:
    * A linear regression model object
    * The training score of the model
    * The testing score of the model
    '''
    # Running Linear Regression
    linreg = LinearRegression()
    linreg.fit(datasets[0], np.ravel(datasets[1]))
    # Printing out train and test accuracy scores
    train_acc = linreg.score(datasets[0], datasets[1])
    test_acc = linreg.score(datasets[2], datasets[3])
    return (linreg, train_acc, test_acc)


def create_model_from_dataset(data_path="combined_flight_data"):
    '''
    Uses flight and weather data to train a classifier and regressor.

    This function trains a classifier model of flight delay probability and a regression model
    of flight delay severity, using the data in the specified file path.

    After training, this function generates a "classifier.pkl" and "regressor.pkl" file containing
    the delay probability and and delay severity models respectively. In addition, produces
    "classifier_metrics.pkl" and "regressor_metrics.pkl" files containing the training score,
    testing score, and (for the classifier) confusion matrix of each their respective models.
    All these files are binary Python pickle objects.

    Parameters
    ----------
    data_path: A path to a pickle file containing a pandas dataframe of flight and weather data.

    Returns
    -------
    None
    '''
    # Reading in the cleaned dataset
    delay_df = pd.read_pickle(data_path)
    processed_datasets = pre_process_dataset(delay_df, target_col=TARGET_COL_CLASSIFIER)
    classifier_modelling_results = train_classifier(processed_datasets)
    processed_datasets = pre_process_dataset(delay_df, target_col=TARGET_COL_REGRESSOR)
    regressor_modelling_results = train_regressor(processed_datasets)
    with open('classifier.pkl','wb') as file:
        pickle.dump(classifier_modelling_results[0],file)
    with open('classifier_metrics.pkl','wb') as file:
        pickle.dump(classifier_modelling_results[1:],file)
    with open('regressor.pkl','wb') as file:
        pickle.dump(regressor_modelling_results[0],file)
    with open('regressor_metrics.pkl','wb') as file:
        pickle.dump(regressor_modelling_results[1:],file)


def predict_delay_probability(predictors):
    '''
    Predicts the probability of a given flight being delayed.

    This function uses the model containined in "classifier.pkl" to predict delay probability.

    Parameters
    ----------
    pred_vector: A vector of flight properties. Must contain the columns used to train the model.

    Returns
    -------
    A float containing the log-probability of a flight delay.
    '''
    with open('classifier.pkl','rb') as file:
        delay_predictor = pickle.load(file)
    with open('encoder.pkl','rb') as file:
        encoder = pickle.load(file)

    print(delay_predictor)
    print(type(delay_predictor))
    net_predictors = predictors[RELEVANT_COLS].copy()

    print(net_predictors)
    encoded_pred = encoder.transform(net_predictors)
    return delay_predictor.predict_proba(encoded_pred)


def get_classifier_metrics():
    '''
    Returns training metrics for "classifier.pkl".
    '''
    with open('classifier_metrics.pkl','rb') as file:
        delay_predictor_metrics = pickle.load(file)
    return delay_predictor_metrics


def predict_delay_severity(predictors):
    '''
    Predicts the time a given flight will be delayed by.

    This function uses the model containined in "regressor.pkl" to predict delay severity.

    Parameters
    ----------
    pred_vector: A vector of flight properties. Must contain the columns used to train the model.

    Returns
    -------
    A float containing the estimated minutes of flight delay.
    '''
    with open('regressor.pkl','rb') as file:
        severity_predictor = pickle.load(file)
    with open('encoder.pkl','rb') as file:
        encoder = pickle.load(file)
    encoded_pred = encoder.transform(predictors)
    return severity_predictor.predict(encoded_pred)


def get_regressor_metrics():
    '''
    Returns training metrics for "regressor.pkl"
    '''
    with open('regressor_metrics.pkl','rb') as file:
        severity_predictor_metrics = pickle.load(file)
    return severity_predictor_metrics

# if __name__ == "__main__":
# create_model_from_dataset(data_path="C:/Users/fioyu/Desktop/UW/DATA515/Project/BTS_Flight_Forecast/flight_forecast/combined_flight_data")