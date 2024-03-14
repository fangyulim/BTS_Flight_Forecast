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
import scipy

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression, LinearRegression

TARGET_COL_CLASSIFIER = "ArrDel15"
TARGET_COL_REGRESSOR = "ArrDelayMinutes"
RELEVANT_COLS = ['Year', 'Month', 'DayofMonth',
                 'Origin', 'temp', 'dewPt', 'day_ind',
                 'rh', 'wdir_cardinal', 'gust', 'wspd', 'pressure', 'wx_phrase']
PICKLE_FOLDER_PATH = "resources/generated/pickles"


def pre_process_dataset(df_to_process, target_col,
                        relevant_columns,
                        encoder_path):
    '''
    Preprocesses flight data for use in training an sklearn model.

    This function takes in a Pandas DataFrame of flight and weather data and pre-processes it by
    by splitting the data into train/test pairs and into target/predictor datasets. The split
    data is then prepared for training by scaling numeric data onto a mean of 0 and variance
    of 1 and by one-hot encoding categorical variables into simple numeric data columns.

    Parameters
    ----------
    df_to_process: A Pandas dataframe containing the data to be pre-processed.
    target_col: The columns that will be the prediction target of the future model
    relevant_columns: The columns that will be used to predict the target
    encoder_path: A path at which to generate an encoder object trained during preprocessing

    Returns
    -------
    A tuple containing, in order:
    * a scipy sparse matrix with training predictor data
    * a Pandas Series with training target data
    * a scipy sparse matrix with testing predictor data
    * a Pandas Series with testing target data
    '''
    if not isinstance(df_to_process, pd.DataFrame):
        raise TypeError("The df_to_process must be a Pandas DataFrame object. Currently it" + \
                        f"is a {type(df_to_process)}.")
    if not target_col in df_to_process.columns.tolist():
        raise ValueError(f"The target column for prediction, {target_col}," +\
                         " must be present in the given dataframe.")
    if not set(relevant_columns).issubset(df_to_process.columns.tolist()):
        raise ValueError(("The relevant columns selected for pre-processing, " + \
                          f"{relevant_columns}, must be present in the given dataframe."))
    if not isinstance(encoder_path, str):
        raise TypeError("The encoder_path must contain a string. This string should contain" + \
                        " the path at which to create a pickled encoder")
    target_series = df_to_process[[target_col]]
    input_df = df_to_process.drop(target_col, axis=1)
    input_df = input_df[relevant_columns]

    x_train, x_test, y_train, y_test = train_test_split(input_df, target_series)

    numeric_cols = x_train.dtypes[(x_train.dtypes == 'int64') | \
                                  (x_train.dtypes == 'float64')].index.tolist()
    non_numeric_cols = x_train.dtypes[(x_train.dtypes != 'int64') & \
                                      (x_train.dtypes != 'float64')].index.tolist()

    encoder = ColumnTransformer([
        ('scaler', StandardScaler(), numeric_cols),
        ('one_hot', OneHotEncoder(drop='first', handle_unknown='ignore'), non_numeric_cols)],
        remainder='drop',
        verbose_feature_names_out=False)

    encoder.fit(x_train)
    x_train_sparse = encoder.transform(x_train)
    # x_train_columns = encoder.get_feature_names_out()
    x_test_sparse = encoder.transform(x_test)
    # x_test_columns = encoder.get_feature_names_out()
    with open(encoder_path, 'wb') as file:
        pickle.dump(encoder, file)

    return (x_train_sparse, y_train,
            x_test_sparse, y_test,)


def train_classifier(datasets):
    '''
    Trains a logistic regression classifier for flight delay probability.

    Parameters
    ----------
    datasets: a tuple containing, in order:
    * a scipy csr_matrix with training predictor data
    * a Pandas DataFrame with training target data
    * a scipy csr_matrix with testing predictor data
    * a Pandas DataFrame with testing target data

    Returns
    -------
    A tuple containing, in order:
    * A logistic regression model object
    * The training score of the model
    * The testing score of the model
    '''
    if len(datasets) != 4:
        raise ValueError("The input dataset must be a collection of 4 elements.")
    if not isinstance(datasets[0], scipy.sparse.csr_matrix) or \
       not isinstance(datasets[2], scipy.sparse.csr_matrix):
        raise TypeError("The elements at indices 0 and 2 of the datasets parameter must be " + \
                        f"scipy csr matrices. They are currently {type(datasets[0])} and " + \
                        f"{type(datasets[2])}, respectively.")
    if not isinstance(datasets[1], pd.DataFrame) or \
       not isinstance(datasets[3], pd.DataFrame):
        raise TypeError("The elements at indices 1 and 3 of the datasets parameter must be " + \
                        f"Pandas DataFrames. They are currently {type(datasets[1])} and " + \
                        f"{type(datasets[3])}, respectively.")
    # Defining logistic regression parameters to sweep over
    logreg_params = {
        'penalty': ['l1', 'l2'],
        'C': [0.1, 1, 10]
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
    if len(datasets) != 4:
        raise ValueError("The input dataset must be a collection of 4 elements.")
    if not isinstance(datasets[0], scipy.sparse.csr_matrix) or \
       not isinstance(datasets[2], scipy.sparse.csr_matrix):
        raise TypeError("The elements at indices 0 and 2 of the datasets parameter must be " + \
                        f"scipy csr matrices. They are currently {type(datasets[0])} and " + \
                        f"{type(datasets[2])}, respectively.")
    if not isinstance(datasets[1], pd.DataFrame) or \
       not isinstance(datasets[3], pd.DataFrame):
        raise TypeError("The elements at indices 1 and 3 of the datasets parameter must be " + \
                        f"Pandas DataFrames. They are currently {type(datasets[1])} and " + \
                        f"{type(datasets[3])}, respectively.")
    # Running Linear Regression
    linreg = LinearRegression()
    linreg.fit(datasets[0], np.ravel(datasets[1]))
    # Printing out train and test accuracy scores
    train_acc = linreg.score(datasets[0], datasets[1])
    test_acc = linreg.score(datasets[2], datasets[3])
    return (linreg, train_acc, test_acc)


def create_model_from_dataset(data_path=PICKLE_FOLDER_PATH+"/combined_flight_data"):
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
    processed_datasets = pre_process_dataset(delay_df,
                                             target_col=TARGET_COL_CLASSIFIER,
                                             relevant_columns=RELEVANT_COLS,
                                             encoder_path=(PICKLE_FOLDER_PATH +
                                                           "/classification_encoder.pkl"))
    classifier_modelling_results = train_classifier(processed_datasets)
    processed_datasets = pre_process_dataset(delay_df,
                                             target_col=TARGET_COL_REGRESSOR,
                                             relevant_columns=RELEVANT_COLS,
                                             encoder_path=(PICKLE_FOLDER_PATH +
                                                           "/regression_encoder.pkl"))
    regressor_modelling_results = train_regressor(processed_datasets)
    with open(PICKLE_FOLDER_PATH + '/classifier.pkl', 'wb') as file:
        pickle.dump(classifier_modelling_results[0], file)
    with open(PICKLE_FOLDER_PATH + '/classifier_metrics.pkl', 'wb') as file:
        pickle.dump(classifier_modelling_results[1:], file)
    with open(PICKLE_FOLDER_PATH + '/regressor.pkl', 'wb') as file:
        pickle.dump(regressor_modelling_results[0], file)
    with open(PICKLE_FOLDER_PATH + '/regressor_metrics.pkl', 'wb') as file:
        pickle.dump(regressor_modelling_results[1:], file)

def predict_delay_probability(predictors,
                              classifier_path = PICKLE_FOLDER_PATH + '/classifier.pkl',
                              encoder_path = PICKLE_FOLDER_PATH + '/classification_encoder.pkl'):
    '''
    Predicts the probability of a given flight being delayed.

    This function uses the model containined in "classifier.pkl" to predict delay probability.

    Parameters
    ----------
    predictors: A Pandas DataFrame of flight properties for which the probability of a delay will
                be predicted. Column names must match those used to train the model.
    classifier_path: A string containing a path to the pickled classifier model.
    encoder_path: A string containing a path to the pickled ColumnTransformer used to preprocess
                  the data for the classifier model

    Returns
    -------
    A list (or collection of lists) containing the log-probability of each given flight being not
    delayed and the log-probability of it being delayed.
    '''
    if not isinstance(predictors, pd.DataFrame):
        raise TypeError("Predictor inputs into the model must be in the form of a Pandas " + \
                        f"DataFrame. Current type is {type(predictors)}, instead.")
    with open(classifier_path, 'rb') as file:
        delay_predictor = pickle.load(file)
    with open(encoder_path, 'rb') as file:
        encoder = pickle.load(file)
    if predictors.columns.shape[0] != encoder.feature_names_in_.shape[0]:
        raise ValueError("Prediction DataFrame must have the same columns used to train" + \
                         f" the model. Predictions have {predictors.columns.shape[0]} " + \
                         "columns while the encoder expects " + \
                         f"{encoder.feature_names_in_.shape[0]}.")
    encoded_pred = encoder.transform(predictors)
    return delay_predictor.predict_proba(encoded_pred)


def get_classifier_metrics(metrics_path = PICKLE_FOLDER_PATH + '/classifier_metrics.pkl'):
    '''
    Returns the training accuracy, testing accuracy, and confusion matrix for the trained
    delay severity regressor.
    '''
    with open(metrics_path, 'rb') as file:
        delay_predictor_metrics = pickle.load(file)
    return delay_predictor_metrics


def predict_delay_severity(predictors):
    '''
    Predicts the time a given flight will be delayed by.

    This function uses the model containined in "regressor.pkl" to predict delay severity.

    Parameters
    ----------
    predictors: A Pandas DataFrame of flight properties for which the probability of a delay will
                be predicted. Column names must match those used to train the model.

    Returns
    -------
    A float (or list of floats) containing the predicted delay in minutes of each given flight.
    '''
    if not isinstance(predictors, pd.DataFrame):
        raise TypeError("Predictor inputs into the model must be in the form of a Pandas " + \
                        f"DataFrame. Current type is {type(predictors)}, instead.")
    with open(PICKLE_FOLDER_PATH + '/regressor.pkl', 'rb') as file:
        severity_predictor = pickle.load(file)
    with open(PICKLE_FOLDER_PATH + '/regression_encoder.pkl', 'rb') as file:
        encoder = pickle.load(file)
    if predictors.columns.shape[0] != encoder.feature_names_in_.shape[0]:
        raise ValueError("Prediction DataFrame must have the same columns used to train" + \
                         f" the model. Predictions have {predictors.columns.shape[0]} " + \
                         "columns while the encoder expects " + \
                         f"{encoder.feature_names_in_.shape[0]}.")
    encoded_pred = encoder.transform(predictors)
    return severity_predictor.predict(encoded_pred)


def get_regressor_metrics():
    '''
    Returns the R-Squared and testing accuracy for the trained delay severity regressor.
    '''
    with open(PICKLE_FOLDER_PATH + '/regressor_metrics.pkl', 'rb') as file:
        severity_predictor_metrics = pickle.load(file)
    return severity_predictor_metrics
