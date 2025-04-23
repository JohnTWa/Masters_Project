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

binary_data = '10110001'
frequency_set = (1, 2)
display_FSK_timing_diagram_labelled(binary_data, frequency_set, T_bit=2)