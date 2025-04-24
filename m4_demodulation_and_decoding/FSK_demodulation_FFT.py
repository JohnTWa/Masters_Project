from _SETUP_ import set_directory
set_directory()
from common.figure_formatting import set_global_font
set_global_font()

import math
import heapq
import numpy as np

from m4_demodulation_and_decoding.FSK.zero_crossing import zero_crossing_count
import m4_demodulation_and_decoding.FSK.FFT as FFT

## Define Filepaths ##
rgb_csv_path = 'files/spreadsheets/s5_rgb_normalised.csv'

## Define signal parameters ##
bits_per_frame      = 8
T_symbol            = 2
frequency_set       = (0.5, 1.0, 1.5, 2.0)
camera_sample_rate  = 60
signal_start_row    = 0

# M-FSK parameters
M                   = len(frequency_set)
bits_per_symbol     = int(math.log2(M))            # =2
symbols_per_frame   = bits_per_frame // bits_per_symbol  # =4

# 1) Compute the full spectrogram once
spec = FFT.compute_fft_spectrogram(
    csv_path=rgb_csv_path,
    column=2,
    consideration_bounds=None,
    sampling_rate=camera_sample_rate,
    window_size=T_symbol*camera_sample_rate,        # tweak for time/freq resolution
    overlap=0
)

FFT.plot_fft_spectrogram(
    spec, 
)

freqs     = spec["frequencies"]       # e.g. array of size ~65
times     = spec["times"]             # time‐centers of each FFT window
intensities = spec["intensity_matrix"]  # shape (len(freqs), len(times))

frame_bits = ''

# 2) For each symbol, pick the time‐bins in [t_start, t_end)
for sym in range(symbols_per_frame):
    # compute time‐range for this symbol
    t_start = sym * T_symbol
    t_end   = t_start + T_symbol
    print(f"Symbol {sym}: {t_start:.1f}s–{t_end:.1f}s")

    # find spectrogram columns that fall in this window
    cols = np.where((times >= t_start) & (times < t_end))[0]
    if len(cols) == 0:
        raise RuntimeError(f"No spectrogram bins for symbol {sym}")

    # average intensity across those columns
    avg_power_per_freq = intensities[:, cols].mean(axis=1)

    # pick the freq bin with maximum power
    peak_idx = int(np.argmax(avg_power_per_freq))
    peak_freq = freqs[peak_idx]

    # map to nearest tone
    tone = min(frequency_set, key=lambda f: abs(f - peak_freq))
    symbol_idx = frequency_set.index(tone)
    bits = format(symbol_idx, f'0{bits_per_symbol}b')
    frame_bits += bits

    print(f"  peak at {peak_freq:.2f} Hz → matched tone {tone} Hz → bits '{bits}'")

print(f"Decoded frame bits: {frame_bits}")