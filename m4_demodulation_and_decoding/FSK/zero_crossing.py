import numpy as np
import pandas as pd

def zero_crossing_count(csv_path, column=0, consideration_bounds=None, sampling_rate=60, threshold=None):
    """
    Counts the number of zero crossings in the selected column of a CSV file.

    :param csv_path: Path to the CSV file containing optical data.
    :param column: Zero-indexed column to consider.
    :param consideration_bounds: Tuple (start_row, end_row) defining row range.
    :param sampling_rate: Sampling rate in Hz (default: 60 Hz).
    :param threshold: Custom threshold for zero-crossing detection (default: mean of signal).
    :return: Number of zero crossings.
    """

    # Load CSV data
    df = pd.read_csv(csv_path)

    # Extract the desired column
    if column >= len(df.columns):
        raise ValueError(f"Column index {column} is out of bounds for CSV with {len(df.columns)} columns.")

    signal = df.iloc[:, column].values

    # Apply consideration bounds if provided
    if consideration_bounds:
        start, end = consideration_bounds
        if start < 0 or end >= len(signal):
            raise ValueError("consideration_bounds out of range.")
        signal = signal[start:end+1]

    # Define zero-crossing threshold (default is signal mean)
    threshold = threshold if threshold is not None else np.mean(signal)

    # Find zero crossings
    crossings = np.where((signal[:-1] - threshold) * (signal[1:] - threshold) < 0)[0]
    num_crossings = len(crossings)

    return num_crossings