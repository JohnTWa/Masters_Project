from _SETUP_ import set_directory
set_directory()

from datetime import datetime
import time
import math
import itertools
import os
import matplotlib.pyplot as plt
from cuesdk import CueSdk

from common.keyboard_interface import keyboard_setup
from common.file_handling import csv_to_tuple
from modulation.ASK_modulation import send_binary_signal

IDs = csv_to_tuple('files/spreadsheets/s1_key_IDs.csv')

def triangle_wave(t, frequency, phase, amplitude=255):
    """
    Returns the value of a triangle wave at time t (in seconds)
    with the given frequency (Hz) and phase (a fractional offset 0.0–1.0).
    The output is in the range 0 to amplitude.
    If frequency is 0 or less, returns 0.
    """
    if frequency is None or frequency <= 0:
        return 0
    T = 1.0 / frequency  # period in seconds
    phase_offset = phase * T
    t_shifted = (t + phase_offset) % T
    if t_shifted < T / 2:
        value = (2 * amplitude / T) * t_shifted
    else:
        value = 2 * amplitude - (2 * amplitude / T) * t_shifted
    return int(round(min(max(value, 0), amplitude)))

def format_timestamp():
    """
    Returns the current time as a formatted string:
    "YYYY-MM-DD-HH-MM-SS-mmm" where mmm is milliseconds.
    """
    now = datetime.now()
    msec = int(now.microsecond / 1000)
    return now.strftime(f"%Y-%m-%d-%H-%M-%S-{msec:03d}")

# -------------------------------------------------------------------
# Transmission Function
# -------------------------------------------------------------------
import math, time, numpy as np
import csv
import matplotlib.pyplot as plt

def colour_variation_test_transmission(IDs, colour_log_path, n_advanced, n_random):
    """
    Sends a series of triangle–wave transmissions to a Corsair device.
    
    Parameters:
      IDs             - iterable of key IDs on which to set the LED colours.
      colour_log_path - path to the log file (e.g., "colour_log.log").
      n_advanced      - number of advanced segments (with out-of-phase/out-of-frequency triangle waves).
      n_random        - number of random-colour segments to send.
    
    The transmission consists of:
      - An initial 5-second segment in which the keyboard is set to red (R=255, G=0, B=0).
      - Basic segments:
          • Triangle waveform in red.
          • Triangle waveform in green.
          • Triangle waveform in blue.
          • Triangle waveforms for red & green, green & blue, red & blue.
          • Triangle waveform in RGB.
      - Fixed-One segments:
          • Keep red fixed at 255; send G, B, and GB waveforms.
          • Keep green fixed at 255; send R, B, and RB waveforms.
          • Keep blue fixed at 255; send R, G, and RG waveforms.
      - Fixed-Two segments:
          • Keep RG fixed at 255; send B waveform.
          • Keep GB fixed at 255; send R waveform.
          • Keep RB fixed at 255; send G waveform.
      - Advanced segments (n_advanced segments as before).
      - Random segments (n_random segments, each 0.2 s, with a constant random colour chosen to maximize variety).
    
    All waveforms use frequencies ≤ 1 Hz. A 0.2-second pause is inserted between segments.
    Each sample is logged with a formatted timestamp, the R, G, B values, and a segment label.
    """
    log_file = open(colour_log_path, "w")
    log_file.write("timestamp,R,G,B,segment\n")
    
    sdk, device_id, CorsairLedColor = keyboard_setup()
    sample_rate = 60  # samples per second
    dt = 1.0 / sample_rate  # sample period in seconds

    # Helper: returns a triangle wave value if freq is not None; otherwise returns the fixed value.
    def get_wave_value(t, params):
        freq, phase = params
        if freq is None:
            return phase
        else:
            return triangle_wave(t, freq, phase)
    
    # --- Initial Segment: Keyboard goes red for 5 seconds ---
    initial_red_segment = {
        'label': 'Initial Red (5 sec)',
        'duration': 5,
        'channels': {'r': (None, 255), 'g': (None, 0), 'b': (None, 0)}
    }
    
    basic_segments = [
        {'label': 'Triangle in red', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (0, 0.0), 'b': (0, 0.0)}},
        {'label': 'Triangle in green', 'duration': 2, 'channels': {'r': (0, 0.0), 'g': (1.0, 0.0), 'b': (0, 0.0)}},
        {'label': 'Triangle in blue', 'duration': 2, 'channels': {'r': (0, 0.0), 'g': (0, 0.0), 'b': (1.0, 0.0)}},
        {'label': 'Triangle in red & green', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (1.0, 0.0), 'b': (0, 0.0)}},
        {'label': 'Triangle in green & blue', 'duration': 2, 'channels': {'r': (0, 0.0), 'g': (1.0, 0.0), 'b': (1.0, 0.0)}},
        {'label': 'Triangle in red & blue', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (0, 0.0), 'b': (1.0, 0.0)}},
        {'label': 'Triangle in RGB', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (1.0, 0.0), 'b': (1.0, 0.0)}},
    ]
    
    red_fixed_segments = [
        {'label': 'Red fixed, G triangle', 'duration': 2, 'channels': {'r': (None, 255), 'g': (1.0, 0.0), 'b': (0, 0.0)}},
        {'label': 'Red fixed, B triangle', 'duration': 2, 'channels': {'r': (None, 255), 'g': (0, 0.0), 'b': (1.0, 0.0)}},
        {'label': 'Red fixed, GB triangle', 'duration': 2, 'channels': {'r': (None, 255), 'g': (1.0, 0.0), 'b': (1.0, 0.0)}},
    ]
    
    green_fixed_segments = [
        {'label': 'Green fixed, R triangle', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (None, 255), 'b': (0, 0.0)}},
        {'label': 'Green fixed, B triangle', 'duration': 2, 'channels': {'r': (0, 0.0), 'g': (None, 255), 'b': (1.0, 0.0)}},
        {'label': 'Green fixed, RB triangle', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (None, 255), 'b': (1.0, 0.0)}},
    ]
    
    blue_fixed_segments = [
        {'label': 'Blue fixed, R triangle', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (0, 0.0), 'b': (None, 255)}},
        {'label': 'Blue fixed, G triangle', 'duration': 2, 'channels': {'r': (0, 0.0), 'g': (1.0, 0.0), 'b': (None, 255)}},
        {'label': 'Blue fixed, RG triangle', 'duration': 2, 'channels': {'r': (1.0, 0.0), 'g': (1.0, 0.0), 'b': (None, 255)}},
    ]
    
    two_fixed_segments = [
        {'label': 'RG fixed, B triangle', 'duration': 2, 'channels': {'r': (None,255), 'g': (None,255), 'b': (1.0,0.0)}},
        {'label': 'GB fixed, R triangle', 'duration': 2, 'channels': {'r': (1.0,0.0), 'g': (None,255), 'b': (None,255)}},
        {'label': 'RB fixed, G triangle', 'duration': 2, 'channels': {'r': (None,255), 'g': (1.0,0.0), 'b': (None,255)}},
    ]
    
    advanced_segments = []
    for i in range(n_advanced):
        norm = i / (n_advanced - 1) if n_advanced > 1 else 0.0
        r_f = 0.5 + 0.5 * ((math.sin(2*math.pi*norm)+1)/2)
        r_p = (math.cos(2*math.pi*norm)+1)/2
        norm_g = ((i + n_advanced/3)/(n_advanced - 1)) if n_advanced > 1 else 0.0
        g_f = 0.5 + 0.5 * ((math.sin(2*math.pi*norm_g)+1)/2)
        g_p = (math.cos(2*math.pi*norm_g)+1)/2
        norm_b = ((i + 2*n_advanced/3)/(n_advanced - 1)) if n_advanced > 1 else 0.0
        b_f = 0.5 + 0.5 * ((math.sin(2*math.pi*norm_b)+1)/2)
        b_p = (math.cos(2*math.pi*norm_b)+1)/2
        
        label = f"Advanced: R(f={r_f:.2f},p={r_p:.2f}) | G(f={g_f:.2f},p={g_p:.2f}) | B(f={b_f:.2f},p={b_p:.2f})"
        seg = {'label': label, 'duration': 2, 'channels': {'r': (r_f, r_p), 'g': (g_f, g_p), 'b': (b_f, b_p)}}
        advanced_segments.append(seg)
    
    random_segments = []
    for i in range(n_random):
        R_rand = int(np.random.randint(0,256))
        G_rand = int(np.random.randint(0,256))
        B_rand = int(np.random.randint(0,256))
        label = f"Random: R={R_rand},G={G_rand},B={B_rand}"
        seg = {'label': label, 'duration': 0.2, 'channels': {'r': (None, R_rand), 'g': (None, G_rand), 'b': (None, B_rand)}}
        random_segments.append(seg)
    
    # Prepend the initial red segment and then combine all segments.
    segments = [initial_red_segment] + basic_segments + red_fixed_segments + green_fixed_segments + blue_fixed_segments + two_fixed_segments + advanced_segments + random_segments
    
    def run_segment(segment):
        label = segment['label']
        duration = segment['duration']
        channels = segment['channels']
        print("Starting segment:", label)
        segment_start = time.time()
        seg_elapsed = 0.0
        while seg_elapsed < duration:
            sample_start = time.time()
            t = seg_elapsed
            r_val = get_wave_value(t, channels.get('r', (0,0.0)))
            g_val = get_wave_value(t, channels.get('g', (0,0.0)))
            b_val = get_wave_value(t, channels.get('b', (0,0.0)))
            led_colors = [CorsairLedColor(id=key_id, r=r_val, g=g_val, b=b_val) for key_id in IDs]
            result = sdk.set_led_colors(device_id, led_colors)
            if result != 0:
                print(f"Warning: set_led_colors error {result} in segment '{label}'.")
            log_line = f"{format_timestamp()},{r_val},{g_val},{b_val},{label}\n"
            log_file.write(log_line)
            log_file.flush()
            elapsed_sample = time.time() - sample_start
            time.sleep(max(0, dt - elapsed_sample))
            seg_elapsed = time.time() - segment_start
        off_colors = [CorsairLedColor(id=key_id, r=0, g=0, b=0) for key_id in IDs]
        sdk.set_led_colors(device_id, off_colors)
    
    def run_pause():
        pause_duration = 0.2
        print("Pausing for 0.2 seconds...")
        pause_start = time.time()
        pause_elapsed = 0.0
        while pause_elapsed < pause_duration:
            sample_start = time.time()
            led_colors = [CorsairLedColor(id=key_id, r=0, g=0, b=0) for key_id in IDs]
            sdk.set_led_colors(device_id, led_colors)
            log_line = f"{format_timestamp()},0,0,0,Pause\n"
            log_file.write(log_line)
            log_file.flush()
            elapsed_sample = time.time() - sample_start
            time.sleep(max(0, dt - elapsed_sample))
            pause_elapsed = time.time() - pause_start
    
    print("Starting colour variation transmission test – logging to", colour_log_path)
    for segment in segments:
        run_segment(segment)
        run_pause()
    log_file.close()
    print("Transmission test complete. Log file saved as:", colour_log_path)
    sdk.disconnect()

# -------------------------------------------------------------------
# Graphing Function
# -------------------------------------------------------------------
def colour_variation_test_transmission_graph(colour_log_path):
    """
    Reads the log file at colour_log_path and plots the red, green, and blue intensities over time.
    
    The x-axis shows the sample index.
    """
    if not os.path.exists(colour_log_path):
        print(f"Log file '{colour_log_path}' not found.")
        return
    
    timestamps = []
    r_vals = []
    g_vals = []
    b_vals = []
    segments = []
    
    with open(colour_log_path, "r") as f:
        next(f)  # Skip the header line.
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            ts, r, g, b, seg = parts
            timestamps.append(ts)
            r_vals.append(int(r))
            g_vals.append(int(g))
            b_vals.append(int(b))
            segments.append(seg)
    
    if not timestamps:
        print("No data found in log file.")
        return
    
    # For plotting, we use the sample index as the x-axis.
    sample_indices = list(range(len(timestamps)))
    
    plt.figure(figsize=(12, 6))
    plt.plot(sample_indices, r_vals, label="Red", color="red")
    plt.plot(sample_indices, g_vals, label="Green", color="green")
    plt.plot(sample_indices, b_vals, label="Blue", color="blue")
    plt.xlabel("Sample Number")
    plt.ylabel("Intensity (0-255)")
    plt.title("Colour Variation Test Transmission")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------
if __name__ == '__main__':

    # keyboard_setup()
    # time.sleep(1) 

    send_binary_signal('1', IDs, 0.5)

    # To run the transmission test, supply a tuple (or list) of key IDs and a path for the log file.
    colour_variation_test_transmission(IDs, "colour_variation_test_transmission.log", 20, 120)
    
    # To plot the graph from the log file, call:
    colour_variation_test_transmission_graph("colour_variation_test_transmission.log")