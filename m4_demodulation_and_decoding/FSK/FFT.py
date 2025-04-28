from _SETUP_ import set_directory
set_directory()
from common.figure_formatting import set_global_font
set_global_font()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.colors import Normalize

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

def plot_three_spectrograms(
    csv_path,
    columns=(0, 1, 2),
    sampling_rate=60,
    window_size=120,
    overlap=0,
    max_freq=2.5,
    scale='dB',
    cmap_list=('Reds', 'Greens', 'Blues'),
    major_fontsize=24,
    minor_fontsize=20,
    vertical_spacing=0.2,
    freq_ticks=[0.5, 1, 1.5, 2]
):
    """
    Compute and plot three vertically stacked spectrograms for R, G, B channels,
    each using its own colormap and individual colorbars.

    :param freq_ticks:
        If provided as a list of numbers, these will be used for y-axis tick locations.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize

    # 1) Compute & transform spectrograms
    specs = []
    for col in columns:
        spec = compute_fft_spectrogram(
            csv_path=csv_path, column=col,
            sampling_rate=sampling_rate,
            window_size=window_size,
            overlap=overlap
        )
        power = spec["intensity_matrix"]
        s = scale.lower()
        if s == 'db':
            data = 10 * np.log10(power + 1e-10)
        elif s == 'amplitude':
            data = np.sqrt(power)
        else:
            data = power / 1e3
        specs.append((spec["times"], spec["frequencies"], data))

    # 2) Normalize color scale up to max_freq
    vmins, vmaxs = [], []
    for _, freqs, data in specs:
        mask = freqs <= max_freq
        vmins.append(data[mask, :].min())
        vmaxs.append(data[mask, :].max())
    norm = Normalize(vmin=min(vmins), vmax=max(vmaxs))

    # 3) Colorbar labels
    if scale.lower() == 'db':
        bar_labels = [r'$P_{\mathrm{R}}$ (dB)',
                      r'$P_{\mathrm{G}}$ (dB)',
                      r'$P_{\mathrm{B}}$ (dB)']
    elif scale.lower() == 'amplitude':
        bar_labels = [r'$A_{\mathrm{R}}$',
                      r'$A_{\mathrm{G}}$',
                      r'$A_{\mathrm{B}}$']
    else:
        bar_labels = [r'$P_{\mathrm{R}}$ ($\times10^3$)',
                      r'$P_{\mathrm{G}}$ ($\times10^3$)',
                      r'$P_{\mathrm{B}}$ ($\times10^3$)']

    # Precompute integer ticks for colorbars
    vmin_int = int(np.floor(norm.vmin))
    vmax_int = int(np.ceil(norm.vmax))

    # 4) Plot
    fig, axes = plt.subplots(
        nrows=3, ncols=1, figsize=(8, 12),
        sharex=True,
        gridspec_kw={'hspace': vertical_spacing}
    )

    for ax, (times, freqs, data), cmap, cbar_label in zip(axes, specs, cmap_list, bar_labels):
        mesh = ax.pcolormesh(times, freqs, data,
                             shading='auto', cmap=cmap, norm=norm)
        ax.set_ylabel(r'$f\ (\mathrm{Hz})$', fontsize=major_fontsize)
        ax.set_ylim(0, max_freq)
        if freq_ticks is not None:
            ax.set_yticks(freq_ticks)
        ax.tick_params(labelsize=minor_fontsize)

        cbar = fig.colorbar(mesh, ax=ax, orientation='vertical', pad=0.02)
        cbar.set_label(cbar_label, fontsize=major_fontsize)
        cbar.set_ticks([vmin_int, vmax_int])
        cbar.set_ticklabels([str(vmin_int), str(vmax_int)])
        cbar.ax.tick_params(labelsize=minor_fontsize)

    axes[-1].set_xlabel('Time (s)', fontsize=major_fontsize)

    # --- NEW: force ticks at 0,2,4,6,8 seconds (and beyond if needed) ---
    import numpy as np
    tN = specs[0][0].max()
    max_tick = max(8, int(np.ceil(tN / 2.0)) * 2)
    ticks = np.arange(0, max_tick + 1e-6, 2)
    axes[-1].set_xticks(ticks)
    axes[-1].set_xlim(0, max_tick)

    # reduce top whitespace, ensure y-labels aren’t cut off
    fig.subplots_adjust(top=0.97, left=0.17)

    plt.show()

if __name__ == '__main__':
    # plot_three_spectrograms('files/spreadsheets/s5_rgb_normalised.csv', scale ='amplitude')
    plot_three_spectrograms('files/spreadsheets/s5_rgb_normalised.csv', scale ='linear')
    plot_three_spectrograms('files/spreadsheets/s5_rgb_normalised.csv', scale ='linear', major_fontsize=18, minor_fontsize=18)
    # plot_three_spectrograms('files/spreadsheets/s5_rgb_normalised.csv', scale ='dB')
# Example Usage:
# result = compute_fft_spectrogram(csv_path, consideration_bounds=(0, 474), sampling_rate=30, window_size=30)
# plot_fft_spectrogram(result)

# result_2 = compute_fft_spectrogram(csv_path, consideration_bounds=(0, 1210), sampling_rate=60, window_size=120, overlap=90)
# plot_3d_waterfall_with_peak_colors(result_2, freq_range=(1,5))
