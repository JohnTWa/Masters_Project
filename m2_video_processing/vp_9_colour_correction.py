import pandas as pd
import numpy as np
import pandas as pd

def inverse_gamma_csv(input_csv, output_csv, gamma=2.2):
    """
    Reads an RGB CSV (no header, columns assumed to be in [0,255]), applies a
    power-law inverse gamma to each value, and writes the result (rounded to
    integers in [0,255]) to output_csv.
    """
    # Load data
    df = pd.read_csv(input_csv, header=None)

    # Apply inverse gamma per column
    for col in df.columns:
        # normalize to [0,1], apply power-law, rescale to [0,255]
        lin = ((df[col] / 255.0) ** gamma) * 255.0
        # clip, round, and convert to integer
        df[col] = lin.clip(0, 255).round().astype(int)

    # Save result
    df.to_csv(output_csv, header=False, index=False)

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

