from _SETUP_ import set_directory
set_directory()

import matplotlib.pyplot as plt
import numpy as np

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

# Example usage
display_synchronous_timing_diagram_labelled(binary_string='10110001', idle_bits=1, major_fontsize=24, minor_fontsize=20)