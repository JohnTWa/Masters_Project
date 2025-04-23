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

def normalise_rgb(
    rgb_averages_csv,
    normalised_rgb_averages_csv,
    n_samples_at_min=30,
    n_samples_at_max=10
):
    """
    Reads an RGB averages CSV (no header), then for each column:
      - Finds the n_samples_at_min-th smallest value and treats it as black (0).
      - Finds the n_samples_at_max-th largest value and treats it as white (255).
      - Linearly scales everything between those two points into [0,255].
      - Clips any values outside to 0 or 255, rounds, and converts to int.
    Saves the result (no header) to normalised_rgb_averages_csv.
    """
    df = pd.read_csv(rgb_averages_csv, header=None)

    for col in df.columns:
        series = df[col]

        # Determine black and white reference levels
        # nth smallest value:
        if n_samples_at_min <= len(series):
            black = series.nsmallest(n_samples_at_min).max()
        else:
            black = series.min()

        # nth largest value:
        if n_samples_at_max <= len(series):
            white = series.nlargest(n_samples_at_max).min()
        else:
            white = series.max()

        # Avoid division by zero
        if white == black:
            df[col] = 0
        else:
            # Scale and clip
            scaled = (series - black) / (white - black) * 255.0
            df[col] = scaled.clip(0, 255).round().astype(int)

    df.to_csv(normalised_rgb_averages_csv, header=False, index=False)