'''
This module uses the unittest framework to run tests on delay_predictor.py.

Within this module the data pre-processing, model training, model prediction, and model metric
reporting functionalities of delay_predictor.py are tested both for typical use and for edge cases.
'''

import unittest
import pandas as pd
import scipy

from utils.delay_predictor import (
    pre_process_dataset,
    train_classifier,
    train_regressor,
    create_model_from_dataset,
    predict_delay_probability,
    get_classifier_metrics,
    predict_delay_severity,
    get_regressor_metrics
) # pylint: disable=import-error

#TARGET_COL_CLASSIFIER = "ArrDel15"
#TARGET_COL_REGRESSOR = "ArrDelayMinutes"
#RELEVANT_COLS = ['Year', 'Month', 'DayofMonth',
#                 'Origin', 'temp', 'dewPt', 'day_ind',
#                 'rh', 'wdir_cardinal', 'gust', 'wspd', 'pressure', 'wx_phrase']
PICKLE_FOLDER_PATH = "resources/testing_resources/pickles"


class TestModelCreation(unittest.TestCase):
    '''
    This class contains and defines the unit tests used on delay_predictor.py
    '''

    # Running smoke tests

    def test_smoke_create_model(self):
        '''
        Tests that create_model_from_dataset, pre_process_dataset, train_classifier, and
        train_regressor all function when called normally.
        '''
        create_model_from_dataset()
        self.assertTrue(True) # pylint: disable=redundant-unittest-assert

    # Running one-shot and pattern tests

    def test_one_shot_preprocess_dataset(self):
        '''
        Tests that data proprocessing occurs correctly for a small sample dataset and that
        the amount of data is preserved after the train-test split.
        '''
        test_df = pd.read_csv("resources/testing_resources/test_date_df.csv")
        result = pre_process_dataset(df_to_process = test_df,
                                     target_col='second_half',
                                     relevant_columns=['year','month','day'],
                                     encoder_path = "resources/testing_resources/encoder.pkl")
        self.assertAlmostEqual(result[0].shape[0] + result[2].shape[0], 50)
        self.assertAlmostEqual(result[1].shape[0] + result[3].shape[0], 50)
        self.assertAlmostEqual(result[0].shape[1], result[2].shape[1])

    def test_one_shot_train_model_classifier(self):
        '''
        Tests that classifier training functions correctly and returns expected metrics
        for a small sample dataset.
        '''
        test_df = pd.read_csv("resources/testing_resources/test_date_df.csv")
        output = pre_process_dataset(df_to_process = test_df,
                                     target_col='second_half',
                                     relevant_columns=['year','month','day'],
                                     encoder_path = "resources/testing_resources/encoder.pkl")
        output = [scipy.sparse.csr_matrix(output[0]),
                  output[1],
                  scipy.sparse.csr_matrix(output[2]),
                  output[3]]
        result = train_classifier(output)
        self.assertGreaterEqual(result[1], 0.5)

    def test_one_shot_train_model_regressor(self):
        '''
        Tests that regressor training functions correctly and returns expected metrics
        for a small sample dataset.
        '''
        test_df = pd.read_csv("resources/testing_resources/test_date_df.csv")
        output = pre_process_dataset(df_to_process = test_df,
                                     target_col='second_half',
                                     relevant_columns=['year','month','day'],
                                     encoder_path = "resources/testing_resources/encoder.pkl")
        output = [scipy.sparse.csr_matrix(output[0]),
                  output[1],
                  scipy.sparse.csr_matrix(output[2]),
                  output[3]]
        result = train_regressor(output)
        self.assertGreaterEqual(result[1], 0.5)

    def test_one_shot_metric_functions(self):
        '''
        Tests that get_classifier_metrics, and get_regressor_metrics run and return the
        correct collection of values.
        '''
        class_scores = get_classifier_metrics()
        reg_scores = get_regressor_metrics()
        self.assertAlmostEqual(len(class_scores), 3)
        self.assertAlmostEqual(len(reg_scores), 2)

    # Running edge case tests

    def test_edge_case_relevant_col_not_in_dataset(self):
        '''
        Tests that the data pre-processing function correctly throws an error when at least
        one of the relevant columns to filter on are not present in the dataset.
        '''
        with self.assertRaises(ValueError):
            test_df = pd.DataFrame(columns=['Year','Month','DayofMonth'])
            test_df.loc[0,:] = [2022, 5, 26]
            pre_process_dataset(test_df, relevant_columns=['Year', 'Week'],
                                target_col="Month",
                                encoder_path = "resources/testing_resources/encoder.pkl")

    def test_edge_case_target_col_not_present(self):
        '''
        Tests that the data pre-processing function correctly throws an error when the
        target value is not present in the dataset.
        '''
        with self.assertRaises(ValueError):
            test_df = pd.DataFrame(columns=['Year','Month','DayofMonth'])
            test_df.loc[0,:] = [2022, 5, 26]
            pre_process_dataset(test_df, relevant_columns=test_df.columns,
                                target_col="ArrDel15",
                                encoder_path = "resources/testing_resources/encoder.pkl")

    def test_edge_case_train_classifier_missing_dataset_entries(self):
        '''
        Tests that the classifier training function properly checks that the dataset contains
        the correct number of matrices/DataFrames.
        '''
        with self.assertRaises(ValueError):
            train_classifier([scipy.sparse.csr_matrix((2, 2)),
                              pd.DataFrame(),
                              scipy.sparse.csr_matrix((2, 2))])

    def test_edge_case_train_regressor_missing_dataset_entries(self):
        '''
        Tests that the regressor training function properly checks that the dataset contains
        the correct number of matrices/DataFrames.
        '''
        with self.assertRaises(ValueError):
            train_classifier([scipy.sparse.csr_matrix((2, 2)),
                              pd.DataFrame(),
                              scipy.sparse.csr_matrix((2, 2))])

    def test_edge_case_train_classifier_invalid_dataset_predictor_data_type(self):
        '''
        Tests that the classifier training function properly checks that the dataset contains
        predictor data in the form of a scipy csr matrix.
        '''
        with self.assertRaises(TypeError):
            train_classifier(["Not a valid sparse matrix",
                              pd.DataFrame(),
                              scipy.sparse.csr_matrix((2, 2)),
                              pd.DataFrame()])

    def test_edge_case_train_classifier_invalid_dataset_target_data_type(self):
        '''
        Tests that the classifier training function properly checks that the dataset contains
        target data in the form of a Pandas DataFrame.
        '''
        with self.assertRaises(TypeError):
            train_classifier([scipy.sparse.csr_matrix((2, 2)),
                              "Not a valid Pandas DataFrame",
                              scipy.sparse.csr_matrix((2, 2)),
                              pd.DataFrame()])

    def test_edge_case_train_regressor_invalid_dataset_predictor_data_type(self):
        '''
        Tests that the regressor training function properly checks that the dataset contains
        predictor data in the form of a scipy csr matrix.
        '''
        with self.assertRaises(TypeError):
            train_regressor(["Not a valid sparse matrix",
                              pd.DataFrame(),
                              scipy.sparse.csr_matrix((2, 2)),
                              pd.DataFrame()])

    def test_edge_case_train_regressor_invalid_dataset_target_data_type(self):
        '''
        Tests that the regressor training function properly checks that the dataset contains
        target data in the form of a Pandas DataFrame.
        '''
        with self.assertRaises(TypeError):
            train_regressor([scipy.sparse.csr_matrix((2, 2)),
                             "Not a valid Pandas DataFrame",
                             scipy.sparse.csr_matrix((2, 2)),
                             pd.DataFrame()])

    def test_edge_case_invalid_query_input_type_classifier(self):
        '''
        Tests that the classification prediction function properly checks that the query is
        given as a Pandas DataFrame.
        '''
        with self.assertRaises(TypeError):
            predict_delay_probability([1,2,3])

    def test_edge_case_invalid_query_input_type_regressor(self):
        '''
        Tests that the regression prediction function properly checks that the query is
        given as a Pandas DataFrame.
        '''
        with self.assertRaises(TypeError):
            predict_delay_severity([1,2,3])

    def test_edge_case_missing_query_columns_classifier(self):
        '''
        Tests that the classification prediction function properly checks that the query has
        the number of columns expected by the encoder and classifier.
        '''
        with self.assertRaises(ValueError):
            test_df = pd.DataFrame(columns=['Year','Month','DayofMonth'])
            predict_delay_probability(test_df)

    def test_edge_case_missing_query_columns_regressor(self):
        '''
        Tests that the regression prediction function properly checks that the query has
        the number of columns expected by the encoder and classifier.
        '''
        with self.assertRaises(ValueError):
            test_df = pd.DataFrame(columns=['Year','Month','DayofMonth'])
            predict_delay_severity(test_df)

    def test_edge_case_preprocess_non_dataframe_input(self):
        '''
        Tests that the pre-processing function properly checks that the data to process is
        in the form of a Pandas DataFrame.
        '''
        with self.assertRaises(TypeError):
            pre_process_dataset([2022, 5, 26], relevant_columns=['Year', 'Week'],
                                target_col="Month",
                                encoder_path = "resources/testing_resources/encoder.pkl")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModelCreation)
    _ = unittest.TextTestRunner().run(suite)
