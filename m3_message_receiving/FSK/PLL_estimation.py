import numpy as np
import pandas as pd

def PLL_estimate(csv_path, column=0, consideration_bounds=None, sampling_rate=60, f_guess=1.0, loop_gain=0.01):
    """
    PLL-based frequency estimation from a CSV column.

    :param csv_path: Path to the CSV file containing optical data.
    :param column: Zero-indexed column to consider.
    :param consideration_bounds: Tuple (start_row, end_row) defining the range of rows to consider.
    :param sampling_rate: Sampling rate in Hz (default: 30 Hz).
    :param f_guess: Initial frequency guess for PLL (default: 1.0 Hz).
    :param loop_gain: PLL loop gain (default: 0.01).
    :return: Estimated dominant frequency.
    """

    # Load the CSV file
    df = pd.read_csv(csv_path)

    # Extract the relevant column
    if column >= len(df.columns):
        raise ValueError(f"Column index {column} is out of bounds for CSV with {len(df.columns)} columns.")

    signal = df.iloc[:, column].values

    # Apply consideration bounds if provided
    if consideration_bounds:
        start, end = consideration_bounds
        if start < 0 or end >= len(signal):
            raise ValueError("consideration_bounds out of range.")
        signal = signal[start:end+1]

    # Time vector based on sampling rate
    dt = 1 / sampling_rate
    time = np.arange(len(signal)) * dt

    # Initial conditions for PLL
    estimated_freq = f_guess
    phase = 0

    # PLL frequency tracking
    for i in range(len(signal)):
        local_oscillator = np.sin(2 * np.pi * estimated_freq * time[i] + phase)
        phase_error = signal[i] * local_oscillator
        estimated_freq += loop_gain * phase_error
        phase += 2 * np.pi * estimated_freq * dt

    return estimated_freq

# Example Usage:
# estimated_frequency = PLL_estimate("optical_data.csv", column=1, consideration_bounds=(100, 500))
# print(f"Estimated Frequency: {estimated_frequency:.3f} Hz")
