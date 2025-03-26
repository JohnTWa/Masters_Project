from _SETUP_ import set_directory
set_directory()

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from data_processing import normalise_rgb, t_t_split, load_rgb_features

def create_CCM(train_features, train_targets):
    """
    Computes a Color Correction Matrix (CCM) using a linear model without intercept.
    """
    X = train_features[['R', 'G', 'B']].values
    Y = train_targets[['R', 'G', 'B']].values

    # Solve X @ M = Y for M (the CCM) using least squares.
    CCM, residuals, rank, s = np.linalg.lstsq(X, Y, rcond=None)
    Y_pred = X @ CCM

    r2 = r2_score(Y, Y_pred, multioutput='uniform_average')
    rmse = np.sqrt(mean_squared_error(Y, Y_pred))
    mae = mean_absolute_error(Y, Y_pred)
    n = X.shape[0]
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - 4)
    
    performance_metrics = {
        'r2': r2,
        'r2_adj': adjusted_r2,
        'rmse': rmse,
        'mae': mae
    }
    
    return CCM, performance_metrics

def create_linear_regression_model(train_features, train_targets):
    '''
    Uses the R, G and B values to create a multiple linear regression model, which is returned as an object.
    Also returns a dictionary of performance metrics with regard to the training data.  
    '''

    # Explicitly select only the 'R', 'G', 'B' columns.
    X_train = train_features[['R', 'G', 'B']].values  # shape (n_samples, 3)
    y_train = train_targets[['R', 'G', 'B']].values   # shape (n_samples, 3)
    
    # Instantiate and fit the linear regression model.
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict on the training data.
    y_pred = model.predict(X_train)
    
    # Compute performance metrics.
    r2 = r2_score(y_train, y_pred, multioutput='uniform_average')
    rmse = np.sqrt(mean_squared_error(y_train, y_pred))
    mae = mean_absolute_error(y_train, y_pred)
    n = X_train.shape[0]
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - 4)
    
    performance_metrics = {
        'r2': r2,
        'r2_adj': adjusted_r2,
        'rmse': rmse,
        'mae': mae
    }

    return(model, performance_metrics)

def create_SVR_model(train_features, train_targets):
    '''
    Uses the R, G and B values to create a Support Vector Regression model using a nonlinear kernel
    Returns the model as an object, and returns a dictionary of training performance metrics.  
    '''

    X_train = train_features[['R', 'G', 'B']].values
    y_train = train_targets[['R', 'G', 'B']].values
    
    model = MultiOutputRegressor(SVR())
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_train)
    r2 = r2_score(y_train, y_pred, multioutput='uniform_average')
    rmse = np.sqrt(mean_squared_error(y_train, y_pred))
    mae = mean_absolute_error(y_train, y_pred)
    n = X_train.shape[0]
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - 4)
    
    performance_metrics = {
        'r2': r2,
        'r2_adj': adjusted_r2,
        'rmse': rmse,
        'mae': mae
    }
    
    return (model, performance_metrics)

def test_CCM(test_features, test_targets, CCM):
    '''
    Tests the CCM to produce a dictionary of performance metrics with regard to the test data. 
    '''
    X_test = test_features[['R', 'G', 'B']].values
    y_test = test_targets[['R', 'G', 'B']].values

    y_pred = X_test @ CCM

    r2 = r2_score(y_test, y_pred, multioutput='uniform_average')
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    n = X_test.shape[0]
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - 4)

    performance_metrics = {
        'r2': r2,
        'r2_adj': adjusted_r2,
        'rmse': rmse,
        'mae': mae
    }
    
    return performance_metrics

def test_regression_model(test_features, test_targets, model): 
    '''
    Tests the regression model to produce a dictionary of performance metrics with regard to the test data.
    '''
    
    X_test = test_features[['R', 'G', 'B']].values
    y_test = test_targets[['R', 'G', 'B']].values
    
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred, multioutput='uniform_average')
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    n = X_test.shape[0]
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - 4)

    performance_metrics = {
        'r2': r2,
        'r2_adj': adjusted_r2,
        'rmse': rmse,
        'mae': mae
    }

    return(performance_metrics)

def correct_rgb_values(normalised_rgb_csv_path, corrected_rgb_values_csv_path, CCM):
    """
    Uses a CCM to correct the normalised RGB values and saves the corrected values to a new CSV.
    The input CSV is assumed to have no header and the first three columns represent R, G, and B.
    """
    df = pd.read_csv(normalised_rgb_csv_path, header=None)
    X = df.iloc[:, :3].values
    corrected = np.dot(X, CCM)
    corrected = np.clip(corrected, 0, 255).round().astype(int)
    df_corrected = pd.DataFrame(corrected)
    df_corrected.to_csv(corrected_rgb_values_csv_path, index=False, header=False)

def predict_rgb_values(rgb_csv_path, predicted_rgb_values_csv_path, model):
    """
    Uses a regression model to produce predicted rgb values from the input rgb csv.
    Predicted values below 0 are set to 0 and values above 255 are set to 255.
    """
    df = pd.read_csv(rgb_csv_path, header=None)
    df_input = pd.DataFrame()
    df_input['R'] = df.iloc[:, 0]
    df_input['G'] = df.iloc[:, 1]
    df_input['B'] = df.iloc[:, 2]

    X = df_input[['R', 'G', 'B']].values
    predictions = model.predict(X)
    
    # Clip predictions to the range 0 to 255 and convert to integers.
    predictions = np.clip(predictions, 0, 255).round().astype(int)
    
    df_pred = pd.DataFrame(predictions, columns=['R', 'G', 'B'])
    df_pred.to_csv(predicted_rgb_values_csv_path, index=False, header=False)

# EXAMPLE USE: 

#filepaths
timestamps_and_colours_path = "files/spreadsheets/frame_timestamps_and_colours.csv"
rgb_csv_path = 'files/spreadsheets/s4_rgb_averages.csv'
normalised_rgb_csv_path = 'files/spreadsheets/s5_rgb_normalised.csv'
corrected_rgb_values_csv_path = 'files/spreadsheets/s6_rgb_corrected.csv'
model_filepath = 'files/p1_regression_model.pkl'

normalise_rgb(rgb_csv_path, normalised_rgb_csv_path)

train_frames, test_frames, train_targets, test_targets = t_t_split(timestamps_and_colours_path, train_proportion=0.7)
train_features, test_features = load_rgb_features(normalised_rgb_csv_path, train_frames, test_frames, key=1)

print('COLOUR CORRECTION MATRIX:')
CCM, training_performance_metrics = create_CCM(train_features, train_targets)
test_performance_metrics = test_CCM(test_features, test_targets, CCM)
print(CCM)
print(f"TRAINING R2: {round(training_performance_metrics['r2'], 3)}, TESTING R2: {round(test_performance_metrics['r2'], 3)}")

print('LINEAR REGRESSOR: ')
l_reg, training_performance_metrics = create_linear_regression_model(train_features, train_targets)
test_performance_metrics = test_regression_model(test_features, test_targets, l_reg)
print(f"TRAINING R2: {round(training_performance_metrics['r2'], 3)}, TESTING R2: {round(test_performance_metrics['r2'], 3)}")

print('SVM: ')
SVM, training_performance_metrics = create_SVR_model(train_features, train_targets)
test_performance_metrics = test_regression_model(test_features, test_targets, SVM)
print(f"TRAINING R2: {round(training_performance_metrics['r2'], 3)}, TESTING R2: {round(test_performance_metrics['r2'], 3)}")

#correct_rgb_values(CCM, normalised_rgb_csv_path, corrected_rgb_values_csv_path)
predict_rgb_values(l_reg, normalised_rgb_csv_path, corrected_rgb_values_csv_path)
print('VALUES SAVED TO ' + normalised_rgb_csv_path)

print('RETRAINING LINEAR REGRESSOR ON COMBINED DATASET...')
train_frames, test_frames, train_targets, _ = t_t_split(timestamps_and_colours_path, train_proportion=1)
train_features, _ = load_rgb_features(normalised_rgb_csv_path, train_frames, test_frames, 1)
l_reg, training_performance_metrics = create_linear_regression_model(train_features, train_targets)
print(f"FINAL R2: {round(training_performance_metrics['r2'], 3)}")
joblib.dump(l_reg, model_filepath)
print('LINEAR REGRESSION MODEL SAVED TO ' + model_filepath)