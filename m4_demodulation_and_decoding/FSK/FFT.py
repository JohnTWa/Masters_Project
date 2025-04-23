from _SETUP_ import set_directory
set_directory()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.art3d import Line3DCollection

csv_path = "files\spreadsheets\s5_rgb_normalised.csv"

def compute_fft_spectrogram(csv_path, column=0, consideration_bounds=None, sampling_rate=60, window_size=120, overlap=0):
    """
    Computes the spectrogram (FFT-based waterfall display).

    :param csv_path: Path to CSV containing optical data.
    :param column: Zero-indexed column to analyze.
    :param consideration_bounds: Tuple (start_row, end_row) defining row range.
    :param sampling_rate: Sampling rate in Hz (default: 30 Hz).
    :param window_size: Size of FFT window (default: 256).
    :param overlap: Overlapping samples between windows (default: 128).
    :return: Dictionary with frequencies, times, and intensity matrix.
    """

    # Load CSV
    df = pd.read_csv(csv_path)

    # Extract desired column
    if column >= len(df.columns):
        raise ValueError(f"Column index {column} is out of bounds for CSV with {len(df.columns)} columns.")

    signal = df.iloc[:, column].values

    # Apply consideration bounds if provided
    if consideration_bounds:
        start, end = consideration_bounds
        if start < 0 or end >= len(signal):
            raise ValueError("consideration_bounds out of range.")
        signal = signal[start:end+1]

    # Compute spectrogram using STFT
    frequencies, times, intensity_matrix = spectrogram(signal, fs=sampling_rate, nperseg=window_size, noverlap=overlap)

    # Return structured output
    return {
        "frequencies": frequencies,
        "times": times,
        "intensity_matrix": intensity_matrix
    }

def plot_fft_spectrogram(result,
                         low_colour="black",
                         mid_colour="purple",
                         high_colour="#fc692b",
                         major_fontsize=24,
                         minor_fontsize=20):
    
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    db_intensity = 10 * np.log10(result["intensity_matrix"] + 1e-10)
    mask = result["frequencies"] <= 5
    vmin = db_intensity[mask, :].min()
    vmax = db_intensity[mask, :].max()

    cmap = LinearSegmentedColormap.from_list(
        'three_color_map',
        [low_colour, mid_colour, high_colour]
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    mesh = ax.pcolormesh(
        result["times"],
        result["frequencies"],
        db_intensity,
        shading='auto',
        cmap=cmap,
        vmin=vmin,
        vmax=vmax
    )
    cbar = plt.colorbar(mesh, ax=ax)
    cbar.set_label('Power (dB)', fontsize=major_fontsize)
    cbar.ax.tick_params(labelsize=minor_fontsize)
    ax.set_xlabel("Time (s)", fontsize=major_fontsize)
    ax.set_ylabel("Frequency (Hz)", fontsize=major_fontsize)
    ax.set_ylim(top=5)
    ax.tick_params(axis='both', labelsize=minor_fontsize)
    plt.tight_layout()
    plt.show()

def plot_3d_waterfall_with_peak_colors(spectrogram_data, colormap=plt.cm.viridis, freq_range=None):
    """
    Generates a 3D waterfall spectrogram where each line has a color gradient, 
    making peaks and troughs visually distinct.

    :param spectrogram_data: Dictionary containing {"frequencies", "times", "intensity_matrix"}
    :param colormap: Matplotlib colormap for power-based color variation.
    :param freq_range: Tuple (min_freq, max_freq) specifying frequency range to display (default: None = all frequencies).
    """

    # Extract spectrogram components
    frequencies = spectrogram_data["frequencies"]
    times = spectrogram_data["times"]
    intensity_matrix = spectrogram_data["intensity_matrix"]

    # Convert power to dB scale
    intensity_matrix_db = 10 * np.log10(intensity_matrix + 1e-10)

    # If a frequency range is specified, filter the frequency bins
    if freq_range is not None:
        min_freq, max_freq = freq_range
        freq_mask = (frequencies >= min_freq) & (frequencies <= max_freq)
        
        frequencies = frequencies[freq_mask]
        intensity_matrix_db = intensity_matrix_db[freq_mask, :]

    # Normalize intensity values for color mapping
    norm = plt.Normalize(np.min(intensity_matrix_db), np.max(intensity_matrix_db))

    # Create a 3D figure
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Create waterfall effect with color variation
    for i, t in enumerate(times):
        z_values = intensity_matrix_db[:, i]  # Power values
        y_values = np.full_like(frequencies, t)  # Constant time for each line
        
        # Normalize colors for this line based on power
        colors = colormap(norm(z_values))  # Different color at peaks/troughs

        # Create segments for Line3DCollection (handles point-wise coloring)
        points = np.array([frequencies, y_values, z_values]).T.reshape(-1, 1, 3)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)  # Line segments

        # Create a Line3DCollection with varying colors
        line = Line3DCollection(segments, cmap=colormap, norm=norm)
        line.set_array(z_values)  # Use power values for coloring
        ax.add_collection3d(line)

    # Labels and title
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Time (s)")
    ax.set_zlabel("Power (dB)")
    ax.set_title(f"3D Waterfall Spectrogram ({freq_range[0]}-{freq_range[1]} Hz)" if freq_range else "3D Waterfall Spectrogram")

    # Adjust viewing angle
    ax.view_init(elev=45, azim=225)

    # Fix: Add colorbar explicitly associated with the figure
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, shrink=0.6, aspect=10, pad=0.1, label="Power (dB)")

    plt.show()

# Example Usage:
result = compute_fft_spectrogram(csv_path, consideration_bounds=(0, 474), sampling_rate=30, window_size=30)
plot_fft_spectrogram(result)

# result_2 = compute_fft_spectrogram(csv_path, consideration_bounds=(0, 1210), sampling_rate=60, window_size=120, overlap=90)
# plot_3d_waterfall_with_peak_colors(result_2, freq_range=(1,5))
