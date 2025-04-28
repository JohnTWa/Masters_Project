from _SETUP_ import set_directory
set_directory()
from common.figure_formatting import set_global_font
set_global_font()

import numpy as np
import matplotlib.pyplot as plt

def display_FSK_timing_diagram_labelled(binary_string, frequency_set, T_bit, SAMPLES_PER_PERIOD=60):
    """
    Displays an FSK timing diagram for the given binary string, with bit values labelled above the waveform
    and vertical dashed lines marking the boundaries between bit segments.
    
    Each bit in binary_string is mapped to a sine wave segment:
      - A '0' is transmitted using frequency_set[0]
      - A '1' is transmitted using frequency_set[1]
    
    For each bit, the number of full sine periods is computed as:
    
        periods = int(T_bit * f)
    
    and the segment duration is:
    
        segment_duration = periods / f
    
    The sine wave for the bit is then computed using numpy.linspace() for the time samples.
    The bit value is placed (using plt.text) at the horizontal midpoint of its segment, just above the waveform.
    Additionally, vertical dashed lines are drawn to mark the boundaries between bit segments.
    
    Parameters:
        binary_string (str): Binary data to be transmitted (e.g., '10110001').
        frequency_set (tuple or list): Two frequencies, where the first is used for a '0' and the second for a '1'.
        T_bit (float, optional): Nominal bit duration (in seconds). Default is 2.
        SAMPLES_PER_PERIOD (int, optional): Number of samples per period for constructing the sine wave. Default is 50.
    """
    
    # Lists to accumulate the time and signal segments,
    # record the horizontal midpoints for labelling, and store boundaries.
    time_segments = []
    signal_segments = []
    bit_midpoints = []
    boundaries = [0]  # initial boundary at time 0
    transmission_length = len(binary_string) * T_bit
    
    current_time = 0  # Running time counter
    for bit in binary_string:
        # Map the bit to its corresponding frequency.
        if bit == '0':
            f = frequency_set[0]
        elif bit == '1':
            f = frequency_set[1]
        else:
            raise ValueError("binary_string must contain only '0' and '1'")
        
        # Compute the number of full periods and the segment duration.
        periods = int(T_bit * f)
        segment_duration = periods / f  # Typically equals T_bit when T_bit * f is an integer
        
        # Generate the time axis for the current bit segment.
        t_segment = np.linspace(0, segment_duration, periods * SAMPLES_PER_PERIOD, endpoint=False)
        # Compute the sine wave (zero phase offset).
        segment_signal = 255*(0.5 + (np.sin(2 * np.pi * f * t_segment))/2)
        
        # Offset the time axis by the current transmission time.
        time_segments.append(current_time + t_segment)
        signal_segments.append(segment_signal)
        
        # Record the horizontal midpoint for labelling.
        midpoint = current_time + segment_duration / 2.0
        bit_midpoints.append(midpoint)
        
        # Update the running time and record the boundary at the end of this bit segment.
        current_time += segment_duration
        boundaries.append(current_time)
    
    # Concatenate all segments.
    t_total = np.concatenate(time_segments)
    signal_total = np.concatenate(signal_segments)

    # Create the plot.
    plt.figure(figsize=(12, 4))
    plt.plot(t_total, signal_total, color='black', linewidth=2)
    plt.xlabel("Time Since Transmission Start (s)", fontsize=24)
    plt.ylabel("LED Red Value \n (0-255)", fontsize=24)
    plt.xticks(fontsize=24)
    plt.yticks([0, 127, 255], fontsize=24)
    plt.ylim(-0.1*255, 255*1.1)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines.bottom.set_bounds(0, transmission_length)
    ax.spines.left.set_bounds(0, 255)
        
    # Draw vertical dashed lines at each boundary.
    for b in boundaries:
        plt.axvline(x=b, linestyle='--', color='black', linewidth=1)
    
    # Label each bit above the waveform (black color) at the midpoint of its segment.
    label_y = 255*1.1  # Vertical position for labels (just above the maximum sine amplitude)
    for i, bit in enumerate(binary_string):
        plt.text(bit_midpoints[i], label_y, bit,
                 ha="center", va="bottom", fontsize=20, color="black")
    
    plt.tight_layout()
    plt.show()

def display_MFSK_timing_diagram_labelled(
    binary_strings,
    frequency_set,
    T_bit,
    SAMPLES_PER_PERIOD=60
):
    """
    Displays an M-FSK timing diagram for R, G, B channels with identical formatting
    to your last version, but with each channel curve using a unique style and thickness.

    :param binary_strings:   Tuple of three bit-strings (R, G, B), each length a multiple of 2.
    :param frequency_set:    Sequence of 4 frequencies for 4-FSK.
    :param T_bit:            Duration in seconds of one FSK symbol (encodes 2 bits).
    :param SAMPLES_PER_PERIOD: Samples per sine period (default 60).
    """
    # Input validation
    if len(binary_strings) != 3:
        raise ValueError("Provide exactly three bit-strings (R, G, B).")
    for bs in binary_strings:
        if len(bs) % 2 != 0 or any(c not in '01' for c in bs):
            raise ValueError("Each bit-string must be binary with even length.")
    
    # Compute symbols & total time
    bits_per_symbol = 2
    n_symbols = len(binary_strings[0]) // bits_per_symbol
    transmission_length = n_symbols * T_bit

    # Boundaries & midpoints
    boundaries = np.arange(n_symbols + 1) * T_bit
    midpoints = boundaries[:-1] + 0.5 * T_bit

    # Build each channel's time & signal
    time_axes, signals = [], []
    for bs in binary_strings:
        t_segs, s_segs = [], []
        current_time = 0.0
        for i in range(n_symbols):
            bit_pair = bs[2*i:2*i+2]
            f = frequency_set[int(bit_pair, 2)]
            periods = int(T_bit * f)
            seg_dur = periods / f
            t_seg = np.linspace(0, seg_dur, periods * SAMPLES_PER_PERIOD, endpoint=False)
            s_seg = 255 * (0.5 + 0.5 * np.sin(2*np.pi * f * t_seg))
            t_segs.append(current_time + t_seg)
            s_segs.append(s_seg)
            current_time += seg_dur
        time_axes.append(np.concatenate(t_segs))
        signals.append(np.concatenate(s_segs))

    # Plot
    plt.figure(figsize=(8, 5))
    colors     = ('red',   '#00BB00',  'blue')
    linestyles = ('-',     '--',     ':')
    linewidths = (3,       2.5,       2)      # thickest to thinnest

    for t, sig, c, ls, lw in zip(time_axes, signals, colors, linestyles, linewidths):
        plt.plot(t, sig, color=c, linewidth=lw, linestyle=ls)

    # Axes labels & ticks
    plt.xlabel("Time (s)", fontsize=24)
    plt.ylabel("LED Colour Value \n (0-255)", fontsize=24)
    plt.xticks(boundaries, fontsize=24)
    plt.yticks([0, 127, 255], fontsize=24)
    plt.ylim(-0.1*255, 255*1.1)
    plt.xlim(-T_bit/6, transmission_length)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_bounds(0, transmission_length)
    ax.spines['left'].set_bounds(0, 255)

    # Symbol boundaries
    for b in boundaries:
        plt.axvline(x=b, linestyle='--', color='black', linewidth=1)

    # Bit-pair labels with increased vertical offsets
    label_y_base = 255 * 1.4
    for idx, bs in enumerate(binary_strings):
        y_offset = idx * 0.15 * 255
        for i in range(n_symbols):
            bit_pair = bs[2*i:2*i+2]
            plt.text(midpoints[i], label_y_base - y_offset, bit_pair,
                     ha="center", va="bottom",
                     fontsize=20, color=colors[idx])

    plt.tight_layout()
    plt.show()

def display_MFSK_timing_diagram_labelled_subplots(
    binary_strings,
    frequency_set,
    T_bit,
    SAMPLES_PER_PERIOD=60,
    subplot_spacing=0.2
):
    """
    Displays an M-FSK timing diagram for R, G, B channels in three stacked subplots,
    with each channel curve using a unique style and thickness, and adjustable vertical spacing.

    :param binary_strings:      Tuple of three bit-strings (R, G, B), each length a multiple of 2.
    :param frequency_set:       Sequence of 4 frequencies for 4-FSK.
    :param T_bit:               Duration in seconds of one FSK symbol (encodes 2 bits).
    :param SAMPLES_PER_PERIOD:  Samples per sine period (default 60).
    :param subplot_spacing:     Float h-space between subplots (default 0.2).
    """
    # Input validation
    if len(binary_strings) != 3:
        raise ValueError("Provide exactly three bit-strings (R, G, B).")
    for bs in binary_strings:
        if len(bs) % 2 != 0 or any(c not in '01' for c in bs):
            raise ValueError("Each bit-string must be binary with even length.")

    # Compute symbols & total time
    bits_per_symbol = 2
    n_symbols = len(binary_strings[0]) // bits_per_symbol
    transmission_length = n_symbols * T_bit

    # Boundaries & midpoints
    boundaries = np.arange(n_symbols + 1) * T_bit
    midpoints = boundaries[:-1] + 0.5 * T_bit

    # Build each channel's time & signal
    time_axes, signals = [], []
    for bs in binary_strings:
        t_segs, s_segs = [], []
        current_time = 0.0
        for i in range(n_symbols):
            bit_pair = bs[2*i:2*i+2]
            f = frequency_set[int(bit_pair, 2)]
            periods = int(T_bit * f)
            seg_dur = periods / f
            t_seg = np.linspace(0, seg_dur, periods * SAMPLES_PER_PERIOD, endpoint=False)
            s_seg = 255 * (0.5 + 0.5 * np.sin(2*np.pi * f * t_seg))
            t_segs.append(current_time + t_seg)
            s_segs.append(s_seg)
            current_time += seg_dur
        time_axes.append(np.concatenate(t_segs))
        signals.append(np.concatenate(s_segs))

    # Prepare subplots
    fig, axes = plt.subplots(3, 1, figsize=(5, 7), sharex=True, facecolor='white')
    # <-- add a left margin so y-labels aren’t clipped
    fig.subplots_adjust(hspace=subplot_spacing)

    colors     = ('red',   'green',  'blue')
    linestyles = ('-',     '-',     '-')
    linewidths = (2,       2,       2)

    # Plot each channel in its own subplot
    for idx, (ax, t, sig, c, ls, lw) in enumerate(zip(axes, time_axes, signals, colors, linestyles, linewidths)):
        ax.plot(t, sig, color=c, linewidth=lw, linestyle=ls)

        # Y-axis formatting
        # ax.set_ylabel(c[0].capitalize(), fontsize=24, rotation=0, labelpad=0)
        ax.set_yticks([0, 255])
        ax.tick_params(axis='y', labelsize=24)
        ax.set_ylim(-0.1*255, 255*1.1)
        # ax.set_ylabel(c[0].capitalize(), fontsize=24, rotation=0, labelpad=-20)

        # X-axis formatting for top two only
        if idx < 2:
            ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
            ax.spines['bottom'].set_visible(False)
        else:
            ax.set_xlabel("Time (s)", fontsize=24)
            ax.set_xticks(boundaries)
            ax.tick_params(axis='x', labelsize=24)
        ax.set_xlim(-T_bit/6, transmission_length)

        # Spine styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_bounds(0, transmission_length)
        ax.spines['left'].set_bounds(0, 255)

        # Symbol boundaries
        for b in boundaries:
            ax.axvline(x=b, linestyle='--', color='black', linewidth=1)

        # Bit-pair labels
        label_y = 255 * 1.1
        for i in range(n_symbols):
            bit_pair = binary_strings[idx][2*i:2*i+2]
            ax.text(midpoints[i], label_y, bit_pair,
                    ha="center", va="bottom",
                    fontsize=20, color=c)

    plt.show()

if __name__ == '__main__':

    display_FSK_timing_diagram_labelled('10110001', (1,2), T_bit=2)
    display_MFSK_timing_diagram_labelled(('10110001', '11001010', '00111001'), (0.5, 1.0, 1.5, 2.0), T_bit=2)
    display_MFSK_timing_diagram_labelled_subplots(('10110001', '11001010', '00111001'), (0.5, 1.0, 1.5, 2.0), T_bit=2)