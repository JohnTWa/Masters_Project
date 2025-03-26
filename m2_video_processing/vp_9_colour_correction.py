import pandas as pd
import numpy as np
import pandas as pd

def normalise_rgb(rgb_averages_csv, normalised_rgb_averages_csv):
    """
    Reads an RGB averages CSV (assumed to have no header) and normalises each column
    so that the minimum value becomes 0 and the maximum value becomes 255. All values
    are converted to integers. The resulting CSV is saved to normalised_rgb_averages_csv.
    """
    df = pd.read_csv(rgb_averages_csv, header=None)
    
    for col in df.columns:
        col_min = df[col].min()
        col_max = df[col].max()
        df[col] = ((df[col] - col_min) / (col_max - col_min) * 255).round().astype(int)
    
    df.to_csv(normalised_rgb_averages_csv, header=False, index=False)

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

if __name__ == "__main__":
    normalise_rgb("files\spreadsheets\s4_rgb_averages.csv", "files\spreadsheets\s5_rgb_normalised.csv")
