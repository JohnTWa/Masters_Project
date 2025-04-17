from _SETUP_ import set_directory
set_directory()

from common.figure_formatting import set_global_font
set_global_font()

import csv
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt

import csv
import matplotlib.pyplot as plt

def plot_BER_vs_f(received_binary_csv, color='black', fontsize=12, x_range=None):
    transmitted    = '10110001'
    bits_per_frame = len(transmitted)

    # Accumulators: for each frequency, total bit‑errors and total bits received
    freq_errors = {}
    freq_bits   = {}

    # Read CSV: columns are [frequency, received_string, _]
    with open(received_binary_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                freq = float(row[0])
                received = row[1].strip()
            except (ValueError, IndexError):
                continue  # skip header or malformed lines

            # Count bit mismatches against the known transmitted pattern
            errors = sum(t != r for t, r in zip(transmitted, received))

            freq_errors[freq] = freq_errors.get(freq, 0) + errors
            freq_bits[freq]   = freq_bits.get(freq,   0) + bits_per_frame

    # Prepare data for plotting, sorted by frequency
    freqs = sorted(freq_errors)
    bers  = [freq_errors[f] / freq_bits[f] for f in freqs]

    # Determine threshold‐line bounds
    if x_range is not None:
        xmin, xmax = x_range
    else:
        xmin, xmax = 10, 30

    # Plot BER curve
    plt.figure()
    plt.plot(freqs, bers, marker='None', color=color)

    # Draw the red dashed threshold only between xmin and xmax
    plt.hlines(y=0.5, xmin=xmin, xmax=xmax, color='r', linestyle='--')

    # Place the label on the threshold line, in red, bold, at 80% of fontsize
    label_fs = fontsize * 0.8
    x_text   = xmin + 0.05 * (xmax - xmin)
    plt.text(
        x_text, 0.5,
        "BER = 0.5 (random guessing)",
        fontsize=label_fs,
        color='red',
        fontweight='bold',
        va='bottom',
        ha='left'
    )

    # Apply x‐range if given
    if x_range is not None:
        plt.xlim(xmin, xmax)

    # Labels and ticks
    plt.xlabel(r'Transmission Frequency $f_{\mathrm{bit}}$ (Hz)', fontsize=fontsize)
    plt.ylabel('Bit Error Rate (BER)', fontsize=fontsize)
    plt.tick_params(axis='both', labelsize=fontsize)

    # Tidy up spines
    ax = plt.gca()
    ax.spines[['right', 'top']].set_visible(False)
    if x_range is not None:
        ax.spines.bottom.set_bounds(xmin, xmax)
    else:
        ax.spines.bottom.set_bounds(min(freqs), max(freqs))
    ax.spines.left.set_bounds(0, 0.5)

    plt.grid(False)

def overlay_BER_vs_f(received_binary_csv, color='orange', linestyle='-'):
    
    transmitted    = '10110001'
    bits_per_frame = len(transmitted)

    freq_errors = {}
    freq_bits   = {}

    with open(received_binary_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                freq = float(row[0])
            except (ValueError, IndexError):
                continue  # skip header or malformed lines

            received = row[1].strip()
            # count bit mismatches
            errors = sum(t != r for t, r in zip(transmitted, received))

            freq_errors[freq] = freq_errors.get(freq, 0) + errors
            freq_bits[freq]   = freq_bits.get(freq,   0) + bits_per_frame

    # sort and compute BER
    freqs = sorted(freq_errors)
    bers  = [freq_errors[f] / freq_bits[f] for f in freqs]

    # overlay plot on existing axes
    plt.plot(freqs, bers,
             color=color,
             marker='None',
             linestyle=linestyle)

if __name__ == "__main__":
    
    folder = 'files/spreadsheets/binary_files'
    list_of_n_keys = [40, 80, 120]

    cmap = mpl.colormaps['Blues']
    colors = cmap(np.linspace(0, 1, len(list_of_n_keys) + 2))

    plot_BER_vs_f(folder + '/binary_1Key_T1.csv', color=colors[1], fontsize=18, x_range=(10, 30))

    for i, n_keys in enumerate(list_of_n_keys):
        overlay_BER_vs_f(folder + f'/binary_{n_keys}Key_T1.csv', color=colors[i + 2])

    plt.tight_layout()
    plt.show()
