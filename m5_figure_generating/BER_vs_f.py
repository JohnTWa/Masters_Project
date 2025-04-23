from _SETUP_ import set_directory
set_directory()

from common.figure_formatting import set_global_font
set_global_font()

import csv
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt

def remove_trailing_zeros_from_column(input_file_path, column_index, output_file_path=None):
    output_file_path = output_file_path or input_file_path

    with open(input_file_path, 'r', encoding='utf-8', newline='') as infile:
        reader = list(csv.reader(infile))

    cleaned_rows = []
    for row in reader:
        # Check if row is long enough
        if column_index < len(row):
            row[column_index] = row[column_index].rstrip('0')
        cleaned_rows.append(row)

    with open(output_file_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(cleaned_rows)

def Hamming_distance(expected_payload, payload):
    # Count the number of bits that are different from the expected payload
    distance = sum([1 for i in range(min(len(expected_payload), len(payload))) if payload[i] != expected_payload[i]])
    # Add missed bits
    missed_bits = len(expected_payload) - len(payload)
    if missed_bits > 0:
        distance += missed_bits  # Pad with zeros if payload is short

    return distance

def calculate_BER(received_payloads, expected_payload, expected_number_of_payloads):    
    # For each received payload:
    errors = 0
    for payload in received_payloads:
        errors += Hamming_distance(expected_payload, payload)
    
    # Include missed frames
    missed_frames = expected_number_of_payloads - len(received_payloads)
    errors += missed_frames * len(expected_payload)

    # Total expected number of bits received
    total_bits_received = expected_number_of_payloads * len(expected_payload)
    
    # Calculate the Bit Error Rate (BER)
    if total_bits_received == 0:
        return 0.0  # Avoid division by zero
    else:
        BER = errors / total_bits_received

    return BER

def create_BER_vs_f_CSV(received_binary_csv, freq_col, payload_col, expected_payload, frames_per_frequency, BER_vs_f_CSV):
    
    frequencies = []
    received_payloads = []
    BERs = []

    # Read CSV: columns are [frequency, received_string, _]
    with open(received_binary_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                frequencies.append(float(row[freq_col]))
                received_payloads.append(row[payload_col].strip())
            except (ValueError, IndexError):
                continue  # skip header or malformed lines
    
    # Calculate BER for each frequency
    frequency_set = set(frequencies)
    for frequency in frequency_set:
        current_frequency_indices = [i for i, freq in enumerate(frequencies) if freq == frequency]
        current_frequency_payloads = [received_payloads[i] for i in current_frequency_indices]
        BERs.append(calculate_BER(current_frequency_payloads, expected_payload, frames_per_frequency))

    # Write to CSV
    with open(BER_vs_f_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for freq, ber in zip(frequency_set, BERs):
            writer.writerow([freq, ber])

def create_BER_vs_f_plot(BER_vs_f_csv, color='black', label='BER', fontsize=16, minor_fontsize=None, xrange=None, yrange=None):
    import csv
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    if minor_fontsize is None:
        minor_fontsize = fontsize * 0.75

    with open(BER_vs_f_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        freqs, BERs = [], []
        for row in reader:
            try:
                f = float(row[0]); b = float(row[1])
            except (ValueError, IndexError):
                continue
            freqs.append(f); BERs.append(b)

    # x‐bounds
    if not xrange:
        xmin, xmax = min(freqs), max(freqs)
    else:
        xmin, xmax = xrange

    # y‐bounds
    if not yrange:
        ymin, ymax = min(BERs), max(BERs)
    else:
        ymin, ymax = yrange

    # filter in both dims
    pairs = zip(freqs, BERs)
    filtered = [(f, b) for f, b in pairs if xmin <= f <= xmax and ymin <= b <= ymax]
    if filtered:
        freqs, BERs = map(list, zip(*filtered))
    else:
        freqs, BERs = [], []

    fig, ax = plt.subplots()
    plt.plot(freqs, BERs, label=label, color=color)
    plt.hlines(0.5, xmin, xmax, color='#A2142F', linestyle='--')
    x_text = xmin + 0.05*(xmax-xmin)
    plt.text(x_text, 0.5, "BER = 0.5 (random guessing)",
             fontsize=minor_fontsize, color='#A2142F', fontweight='bold',
             va='bottom', ha='left')

    # formatting & limits
    plt.xlabel(r'Transmission Frequency $f_{\mathrm{bit}}$ (Hz)', fontsize=fontsize)
    plt.ylabel('Bit Error Rate (BER)', fontsize=fontsize)
    plt.tick_params(axis='both', labelsize=minor_fontsize)

    ax.spines[['right','top']].set_visible(False)
    ax.spines.bottom.set_bounds(xmin, xmax)
    ax.spines.left.set_bounds(ymin, ymax)

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    return fig, ax

def add_to_BER_vs_f_plot(BER_vs_f_csv, color='orange', label='BER'):
    
    with open(BER_vs_f_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        # Read data into lists
        freqs = []
        BERs  = []
        for row in reader:
            try:
                freq = float(row[0])
                BER  = float(row[1])
            except (ValueError, IndexError):
                continue
        
            freqs.append(freq)
            BERs.append(BER)
        
    xmin = min(freqs)
    xmax = max(freqs)
        
    plt.plot(freqs, BERs, marker='None', color=color, label=label)

def add_right_legend(fig, ax, minor_fontsize=12):
    
    lines, labels = ax.get_legend_handles_labels()
    fig.subplots_adjust(right=0.75)
    
    # Retrieve legend handles and labels from the axis.
    lines, labels = ax.get_legend_handles_labels()
    if lines and labels:
        fig.legend(lines, labels,
                    loc='center right',
                    bbox_to_anchor=(1, 0.5),
                    ncol=1,
                    frameon=False, 
                    fontsize=minor_fontsize)
    else: 
        print("No legend handles and labels found in the axis.")

    return fig, ax

def add_top_legend(fig, ax, ncol_max=4, minor_fontsize=12):
    
    # Legend is required:
    legend = True
    new_bottom = 0.15 
    pos = ax.get_position()

    # Retrieve legend handles and labels from the axis.
    lines, labels = ax.get_legend_handles_labels()
    if len(lines) > ncol_max:  # two-row legend
        ncol = ncol_max
        new_height = pos.height * 0.92
        legend_y = (new_bottom + new_height) * 1.15
    else:  # single-row legend
        ncol = len(lines)
        new_height = pos.height * 0.9
        legend_y = (new_bottom + new_height) * 1.15

    # Adjust the axis position to make room for the legend
    ax.set_position([pos.x0, new_bottom, pos.width, new_height])

    # Create the legend on the figure rather than the axes
    fig.legend(lines, labels,
                loc='upper center',
                bbox_to_anchor=(0.5, legend_y),
                ncol=ncol, 
                frameon=False, 
                fontsize=minor_fontsize)
    
    return fig, ax

if __name__ == "__main__":
    
    binary_files_directory = 'files/spreadsheets/binary_files'
    BER_vs_f_directory = 'files/spreadsheets/BER_vs_f'
    list_of_n_keys = [40, 80, 120]

    cmap = mpl.colormaps['Blues']
    colors = cmap(np.linspace(0, 1, len(list_of_n_keys) + 3))

    remove_trailing_zeros_from_column(binary_files_directory + '/binary_1Key_T1.csv', 1)
    create_BER_vs_f_CSV(
        received_binary_csv= binary_files_directory+'/binary_1Key_T1.csv',
        freq_col=0,
        payload_col=1,
        expected_payload='10110001',
        frames_per_frequency=40,
        BER_vs_f_CSV= BER_vs_f_directory+'/asynch_1Key.csv', 
    )
    fig, ax = create_BER_vs_f_plot(
        BER_vs_f_csv=BER_vs_f_directory+'/asynch_1Key.csv', 
        color=colors[2], 
        xrange=(10, 30), 
        yrange=(0,0.6), 
        label='1 key', 
        fontsize=16
    )
    for i, n_keys in enumerate(list_of_n_keys):
        remove_trailing_zeros_from_column(binary_files_directory + f'/binary_{n_keys}Key_T1.csv', 1)

        create_BER_vs_f_CSV(
            received_binary_csv= binary_files_directory + f'/binary_{n_keys}Key_T1.csv',
            freq_col=0,
            payload_col=1,
            expected_payload='10110001',
            frames_per_frequency=20,
            BER_vs_f_CSV= BER_vs_f_directory+f'/asynch_{n_keys}Key.csv'
        )
        add_to_BER_vs_f_plot(BER_vs_f_directory+f'/asynch_{n_keys}Key.csv', color=colors[i+3], label=f'{n_keys} keys')

    plt.tight_layout()
    fig, ax = add_top_legend(fig, ax, minor_fontsize=12)
    fig.set_size_inches(5, 5)
    plt.grid(True)
    plt.show()

    fig, ax = create_BER_vs_f_plot(BER_vs_f_csv='files/spreadsheets/BER_vs_f/synch.csv', color='#228B22', yrange=(0,0.6))
    plt.tight_layout()
    fig.set_size_inches(5, 4.5)
    plt.grid(True)
    plt.show()