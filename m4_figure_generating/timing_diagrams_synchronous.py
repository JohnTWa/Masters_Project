from _SETUP_ import set_directory
set_directory()

from common.figure_formatting import set_global_font
set_global_font()

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def display_synchronous_timing_diagram_labelled(binary_string, idle_bits, major_fontsize, minor_fontsize):
    """
    Displays a synchronous communication timing diagram for a binary frame with three signals:
      1. EN: Constant high (1) during the active region and off (0) during idle bits.
      2. CLK: A clock signal that toggles at the midpoint of each active bit; 0 during idle bits.
      3. DATA0: A step function representing the binary message during the active region; 0 during idle bits.
    
    The frame is padded on both sides with idle bits (where all lines are off).  
    Idle bits are not labelled (even in the DATA0 subplot).  
    The x-axis is in bit positions.
    """
    # Basic parameters.
    bit_duration = 1
    N = len(binary_string)                   # Number of active bits.
    total_bits = idle_bits + N + idle_bits     # Total bits including idle padding.

    # Create an extended binary string for the DATA0 signal (idle bits are '0').
    extended_binary = "0" * idle_bits + binary_string + "0" * idle_bits

    # ----- EN Signal -----
    # For EN, we want it to be high (1) only during the active region.
    t_EN = np.linspace(0, total_bits, total_bits + 1)
    EN = np.array([1 if idle_bits <= i < idle_bits + N else 0 for i in range(total_bits + 1)])

    # ----- DATA0 Signal -----
    # Build a step function from the extended binary string.
    t_msg = []
    msg_vals = []
    for i, bit in enumerate(extended_binary):
        t_msg.extend([i * bit_duration, (i + 1) * bit_duration])
        msg_vals.extend([int(bit), int(bit)])

    # ----- CLK Signal -----
    # Generate a clock only for the active region.
    # First, build the active region clock (shifted by idle_bits).
    active_midpoints = [(i + 0.5) * bit_duration for i in range(N)]
    active_t_clk = [idle_bits] + [idle_bits + m for m in active_midpoints]
    active_y_clk = [0]
    for i in range(N):
        # Toggle: For even-indexed active bits, the clock goes high.
        active_y_clk.append(1 if i % 2 == 0 else 0)
    # Ensure the clock ends at 0.
    if active_y_clk[-1] == 1:
        active_t_clk.append(idle_bits + N)
        active_y_clk.append(0)
    
    # Now build the full CLK signal:
    # - Before the active region (from 0 to idle_bits), CLK is 0.
    # - After the active region (from idle_bits+N to total_bits), CLK is 0.
    t_clk = [0, idle_bits] + active_t_clk[1:] + [total_bits]
    y_clk = [0, 0] + active_y_clk[1:] + [0]

    # ----- Plotting -----
    # Create a figure with 3 subplots sharing the same x-axis.
    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(12, 8))
    
    # Plot EN.
    axs[0].step(t_EN, EN, where='post', color='black', linewidth=2)
    axs[0].set_ylim(-0.2, 1.2)
    axs[0].set_ylabel("EN", fontsize=major_fontsize)
    axs[0].set_yticks([0, 1], ["OFF", "ON"])  # Changed here
    axs[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    axs[0].spines.top.set_visible(False)
    axs[0].spines.right.set_visible(False)
    axs[0].spines.bottom.set_visible(False)
    axs[0].spines.left.set_bounds(0, 1)
    
    # Plot CLK.
    axs[1].step(t_clk, y_clk, where='post', color='black', linewidth=2)
    axs[1].set_ylim(-0.2, 1.2)
    axs[1].set_ylabel("CLK", fontsize=major_fontsize)
    axs[1].set_yticks([0, 1], ["OFF", "ON"])  # Changed here
    axs[1].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    axs[1].spines.top.set_visible(False)
    axs[1].spines.right.set_visible(False)
    axs[1].spines.bottom.set_visible(False)
    axs[1].spines.left.set_bounds(0, 1)
    
    # Plot DATA0.
    axs[2].step(t_msg, msg_vals, where='post', color='black', linewidth=2)
    axs[2].set_ylim(-0.2, 1.2)
    axs[2].set_ylabel("DATA0", fontsize=major_fontsize)
    axs[2].set_yticks([0, 1], ["OFF", "ON"])  # Changed here
    axs[2].set_xticks(np.arange(0, total_bits + 1, 1))
    axs[2].set_xlabel("Bit Position", fontsize=major_fontsize)
    axs[2].spines.top.set_visible(False)
    axs[2].spines.right.set_visible(False)
    axs[2].spines.bottom.set_bounds(0, total_bits)
    axs[2].spines.left.set_bounds(0, 1)
    
    # Label only the active bits in the DATA0 subplot.
    for idx, bit in enumerate(binary_string):
        x_pos = idle_bits + idx + 0.5  # Shift label into the active region.
        y_pos = int(bit)
        axs[2].text(x_pos, y_pos + 0.1, str(bit),
                    ha='center', fontsize=minor_fontsize, color='black')
    
    # Apply tick label size to all subplots.
    for ax in axs:
        ax.tick_params(axis='both', which='major', labelsize=major_fontsize)
    
    plt.tight_layout()
    plt.show()

def display_synchronous_received(bit_freq, rgb_csv, SGL_column, CLK_column, DATA_column, sample_rate, start_row, major_fontsize, normalise=False):
    # Calculate total frame duration (10 bits: 8 bits + 2 idle bits).
    total_bits = 10
    duration = total_bits / bit_freq  # Duration in seconds.
    n_samples = int(sample_rate * duration)  # Number of samples corresponding to the duration.

    # Read CSV (no header) and extract the rows, skipping the first `start_row` rows.
    df = pd.read_csv(rgb_csv, header=None)
    df_sampled = df.iloc[start_row : start_row + n_samples, :]

    # Create the time axis. Each sample is 1/sample_rate seconds apart.
    t = np.arange(n_samples) / sample_rate

    # Create figure with 3 subplots sharing the same x-axis.
    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(12, 8))

    # Define the fixed y-axis limits and ticks.
    fixed_ylim = (-51, 306)
    fixed_yticks = [0, 255]

    # ----- SGL Subplot -----
    y_SGL = df_sampled.iloc[:, SGL_column]
    if normalise:
        min_val = y_SGL.min()
        max_val = y_SGL.max()
        if max_val != min_val:
            y_SGL = (y_SGL - min_val) / (max_val - min_val) * 255
        else:
            y_SGL = y_SGL * 0
    axs[0].plot(t, y_SGL, color='black', linewidth=2)
    axs[0].set_ylabel("SGL", fontsize=major_fontsize)
    axs[0].set_ylim(fixed_ylim)
    axs[0].set_yticks(fixed_yticks)
    axs[0].spines.top.set_visible(False)
    axs[0].spines.right.set_visible(False)
    # Remove bottom spine and adjust left spine bounds.
    axs[0].spines.bottom.set_visible(False)
    axs[0].spines.left.set_bounds(fixed_yticks[0], fixed_yticks[1])
    # Hide x-axis tick labels.
    axs[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # ----- CLK Subplot -----
    y_CLK = df_sampled.iloc[:, CLK_column]
    if normalise:
        min_val = y_CLK.min()
        max_val = y_CLK.max()
        if max_val != min_val:
            y_CLK = (y_CLK - min_val) / (max_val - min_val) * 255
        else:
            y_CLK = y_CLK * 0
    axs[1].plot(t, y_CLK, color='black', linewidth=2)
    axs[1].set_ylabel("CLK", fontsize=major_fontsize)
    axs[1].set_ylim(fixed_ylim)
    axs[1].set_yticks(fixed_yticks)
    axs[1].spines.top.set_visible(False)
    axs[1].spines.right.set_visible(False)
    # Remove bottom spine and adjust left spine bounds.
    axs[1].spines.bottom.set_visible(False)
    axs[1].spines.left.set_bounds(fixed_yticks[0], fixed_yticks[1])
    # Hide x-axis tick labels.
    axs[1].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # ----- DATA0 Subplot -----
    y_DATA = df_sampled.iloc[:, DATA_column]
    if normalise:
        min_val = y_DATA.min()
        max_val = y_DATA.max()
        if max_val != min_val:
            y_DATA = (y_DATA - min_val) / (max_val - min_val) * 255
        else:
            y_DATA = y_DATA * 0
    axs[2].plot(t, y_DATA, color='black', linewidth=2)
    axs[2].set_ylabel("DATA0", fontsize=major_fontsize)
    axs[2].set_ylim(fixed_ylim)
    axs[2].set_yticks(fixed_yticks)
    axs[2].set_xlabel("Time (s)", fontsize=major_fontsize)
    axs[2].spines.top.set_visible(False)
    axs[2].spines.right.set_visible(False)
    # Adjust bottom spine to span the full x-axis range and left spine bounds.
    axs[2].spines.bottom.set_bounds(t[0], t[-1])
    axs[2].spines.left.set_bounds(fixed_yticks[0], fixed_yticks[1])

    # Calculate T_bit (duration of one bit) and set x-axis ticks in intervals of T_bit.
    T_bit = 1 / bit_freq
    xticks = np.arange(t[0], t[-1] + T_bit, T_bit)
    axs[2].set_xticks(xticks)

    # Apply tick label size to all subplots.
    for ax in axs:
        ax.tick_params(axis='both', which='major', labelsize=major_fontsize)

    plt.tight_layout()
    plt.show()
    
# Example usage
display_synchronous_timing_diagram_labelled(binary_string='10110001', idle_bits=1, major_fontsize=24, minor_fontsize=20)
display_synchronous_received(bit_freq=10, rgb_csv='files/spreadsheets/s5_rgb_normalised.csv', SGL_column=3, CLK_column=0, DATA_column=6, sample_rate=67, start_row=125, major_fontsize=24, normalise=True)