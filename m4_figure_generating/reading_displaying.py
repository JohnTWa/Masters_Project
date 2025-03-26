from _SETUP_ import set_directory
set_directory()

import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

def display_binary_reading_with_markers(reading_csv_path):
    """
    Reads a CSV file containing signal data and visualizes it, including markers for flips, toggle sequences,
    message bounds, pauses, and signals.

    Parameters:
    - reading_csv_path (str): Path to the input CSV containing signal data.
    """
    values = []
    row_numbers = []
    up_markers = []
    down_markers = []
    repeat_markers = []
    up_rows = []
    down_rows = []
    repeat_rows = []
    msg_start_indices = []
    msg_end_indices = []
    pause_start_indices = []
    pause_end_indices = []
    signal_start_indices = []
    signal_end_indices = []

    try:
        with open(reading_csv_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header row

            # Dynamically identify column indices based on headers
            try:
                value_index = header.index("Value")
                change_type_index = header.index("Change Type")
                message_bounds_index = next((i for i, col in enumerate(header) if "Message Bounds" in col), None)
                pause_index = next((i for i, col in enumerate(header) if "Pause" in col), None)
                signal_index = next((i for i, col in enumerate(header) if "Signal" in col), None)
            except ValueError as e:
                print(f"Error: Missing required column headers. {e}")
                return

            # Extract data row by row
            for i, row in enumerate(reader):
                row_num = i + 2  # Account for 1-based indexing and header row
                try:
                    # Extract signal value
                    value = float(row[value_index])
                    values.append(value)
                    row_numbers.append(row_num)
                    
                    # Process flip state
                    flip_state = row[change_type_index].strip().lower()
                    if flip_state == "up":
                        up_markers.append(value)
                        up_rows.append(row_num)
                    elif flip_state == "down":
                        down_markers.append(value)
                        down_rows.append(row_num)
                    elif flip_state == "repeat":
                        repeat_markers.append(value)
                        repeat_rows.append(row_num)

                    # Process message bounds
                    if message_bounds_index is not None:
                        message_marker = row[message_bounds_index].strip().lower()
                        if "start" in message_marker and "message" in message_marker:
                            msg_start_indices.append(row_num)
                        elif "end" in message_marker and "message" in message_marker:
                            msg_end_indices.append(row_num)

                    # Process pause bounds
                    if pause_index is not None:
                        pause_marker = row[pause_index].strip().lower()
                        if "start" in pause_marker and "pause" in pause_marker:
                            pause_start_indices.append(row_num)
                        elif "end" in pause_marker and "pause" in pause_marker:
                            pause_end_indices.append(row_num)

                    # Process signal bounds
                    if signal_index is not None:
                        signal_marker = row[signal_index].strip().lower()
                        if "start" in signal_marker and "signal" in signal_marker:
                            signal_start_indices.append(row_num)
                        elif "end" in signal_marker and "signal" in signal_marker:
                            signal_end_indices.append(row_num)

                except (ValueError, IndexError):
                    continue  # Skip invalid rows

        # Plot the data
        plt.figure(figsize=(12, 4))
        plt.plot(row_numbers, values, linestyle='-', color='b', label='Reading')  # Line-only plot for the data
        plt.scatter(up_rows, up_markers, color='g', marker='^', label='Flip Up', zorder=5)  # Green triangles for "up"
        plt.scatter(down_rows, down_markers, color='r', marker='v', label='Flip Down', zorder=5)  # Red inverted triangles for "down"
        plt.scatter(repeat_rows, repeat_markers, color='orange', marker='o', label='Repeat', zorder=5)  # Orange circles for "repeat"

        # Highlight message bounds with vertical spans
        for start, end in zip(msg_start_indices, msg_end_indices):
            plt.axvspan(start, end, color='lightgreen', alpha=0.3, label='Message Bounds')

        # Highlight pauses with vertical spans
        for start, end in zip(pause_start_indices, pause_end_indices):
            plt.axvspan(start, end, color='brown', alpha=0.3, label='Pause')

        # Highlight signals with vertical spans
        for start, end in zip(signal_start_indices, signal_end_indices):
            plt.axvspan(start, end, color='purple', alpha=0.3, label='Signal')

        # Prevent duplicate labels in the legend
        handles, labels = plt.gca().get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))
        plt.legend(unique_labels.values(), unique_labels.keys())

        plt.title('Reading vs. Row Number')
        plt.xlabel('Row Number')
        plt.ylabel('Reading')
        plt.grid(True)
        plt.show()

    except FileNotFoundError:
        print(f"Error: File not found at {reading_csv_path}.")
    except Exception as e:
        print(f"Unexpected error: {e}")

from matplotlib.ticker import FuncFormatter

def display_binary_reading(reading_csv_path, consideration_bounds=None, framerate=60, start_time=None, value_interval=1):
    """
    Reads a CSV file containing signal data and visualizes it without any markers for areas, flips, or annotations.
    
    Parameters:
    - reading_csv_path (str): Path to the input CSV containing signal data.
    - consideration_bounds (tuple, optional): Tuple (start_row, end_row) to limit visualization to specific rows.
      Row numbers are 1-indexed.
    - framerate (int): Framerate in Hz to convert row numbers into time (default is 60 Hz).
    - start_time (float, optional): The starting time (in seconds) for the x-axis labels.
      If not specified, it defaults to the time corresponding to the first data point within consideration_bounds.
    - value_interval (float, optional): Interval in seconds between x-axis ticks (default is 1 second).
    """
    values = []
    times = []

    try:
        with open(reading_csv_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header row

            try:
                value_index = header.index("Value")
            except ValueError:
                print("Error: Missing required 'Value' column in the header.")
                return

            for i, row in enumerate(reader):
                row_num = i + 2  # Account for 1-based indexing and header row
                if consideration_bounds:
                    start_row, end_row = consideration_bounds
                    if row_num < start_row or row_num > end_row:
                        continue
                try:
                    value = float(row[value_index])
                    time = (row_num - 1) / framerate  # Convert row number to time in seconds
                    values.append(value)
                    times.append(time)
                except (ValueError, IndexError):
                    continue  # Skip invalid rows

        if not values:
            print("No data to display within the specified consideration bounds.")
            return

        original_start_time = times[0]
        if start_time is None:
            start_time = original_start_time
        shift = start_time - original_start_time

        def shifted_formatter(x, pos):
            return f"{x + shift:.1f}"

        dpi = 100  # Dots per inch
        width = 1000 / dpi  # Convert pixels to inches
        height = 300 / dpi

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        plt.plot(times, values, linestyle='-', color='black')  # Line-only plot for the data
        plt.ylim(min(values) - 1, max(values) + 1)  # Add padding to the y-axis
        plt.xlabel("Time Since Video Start (s)")
        plt.ylabel("Red Value (0-255)")
        plt.grid(False)  # Turn off gridlines
        plt.tight_layout()  # Adjust layout to prevent clipping

        plt.gca().xaxis.set_major_formatter(FuncFormatter(shifted_formatter))

        # Define tick labels
        min_time = times[0]
        max_time = times[-1]
        ticks = np.arange(min_time, max_time + value_interval, value_interval)
        tick_labels = ticks + shift
        plt.xticks(ticks, [f"{t:.1f}" for t in tick_labels])

        plt.show()

    except FileNotFoundError:
        print(f"Error: File not found at {reading_csv_path}.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def display_FSK_reading(csv_path, column, framerate=None):
    """
    Reads a specified column of numeric data from csv_path and displays its
    value over time using Matplotlib, with a white background and black curve.
    The y-axis is fixed to always range from 0 to 255.
    
    Parameters:
    - csv_path (str): Path to the CSV file containing numeric data in columns.
    - column (int): 0-based column index to read.
    - framerate (float, optional): Frames per second (used to convert row index
      to time in seconds).
    """
    import csv
    import matplotlib.pyplot as plt
    import numpy as np

    # 1) Read values from the specified column
    values = []
    with open(csv_path, 'r', newline='') as infile:
        reader = csv.reader(infile)
        for row_index, row in enumerate(reader):
            if len(row) <= column:
                # Skip rows that do not have enough columns
                continue
            try:
                val = float(row[column])
                values.append(val)
            except ValueError:
                # Skip rows where the value is not numeric
                continue

    if not values:
        print(f"No valid data found in column {column} of '{csv_path}'")
        return

    # 2) Create a time axis based on row index
    video_frames = list(range(len(values)))

    # 3) Plot the data
    plt.figure(figsize=(12, 4), facecolor='white')  # White background
    plt.plot(video_frames, values, linestyle='-', color='black', linewidth=2)  # Black curve

    # 4) Set Y limits fixed to 0 and 255
    plt.ylim(0, 255)

    # 5) Label and style the axes
    if framerate:
        plt.xlabel("Time Since Video Start (s)", fontsize=24)
        plt.xticks(np.arange(0, len(video_frames), framerate),
                   labels=np.arange(0, len(video_frames) / framerate).astype(int),
                   fontsize=24)
    else:
        plt.xlabel("Video Frame", fontsize=24)
        plt.xticks(fontsize=24)
    plt.ylabel("Received Red Value \n (0-255)", fontsize=24)
    # Set fixed y-ticks at 0, 128, and 255 for clarity
    plt.yticks([0, 128, 255], fontsize=24)

    # Disable the grid for a clean, white-background look
    plt.grid(False)

    # 6) Tight layout to prevent label clipping and adjust spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines.bottom.set_bounds(0, len(video_frames))
    ax.spines.left.set_bounds(0, 255)

    plt.tight_layout()
    plt.show()

def display_ASK_reading(csv_path, column, framerate, compression_factor=0.5):
    import csv
    import matplotlib.pyplot as plt
    import numpy as np

    # 1) Read the values from the specified column in the CSV file.
    values = []
    with open(csv_path, 'r', newline='') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if len(row) <= column:
                continue  # Skip rows that do not have enough columns
            try:
                values.append(float(row[column]))
            except ValueError:
                continue  # Skip rows where the value is not numeric

    if not values:
        print(f"No valid data found in column {column} of '{csv_path}'")
        return

    # 2) Create a time axis in seconds (one time unit per frame).
    time_axis = np.arange(len(values)) / framerate

    # 3) Compute parameters for vertical compression.
    full_range = 255.0
    new_range = compression_factor * full_range
    offset = (full_range - new_range) / 2  # Center the compressed data vertically

    # 4) Transform the original data so it occupies only the compressed (central) region.
    values_compressed = np.array(values) * compression_factor + offset

    # 5) Create the plot.
    plt.figure(figsize=(12, 4), facecolor='white')
    plt.plot(time_axis, values_compressed, linestyle='-', color='black', linewidth=2)

    # 6) Set overall y-axis limits to 0-255 (so nothing shifts horizontally).
    plt.ylim(0, full_range)

    # 7) Set x-axis ticks at intervals of 0.2 seconds (ensuring none extend beyond the data).
    max_time = time_axis[-1]
    xticks = np.arange(0, max_time + 0.2, 0.2)
    xticks = xticks[xticks <= max_time]
    plt.xticks(xticks, fontsize=24)
    plt.xlabel("Time Since Video Start (s)", fontsize=24)

    # 8) Compute y-axis tick positions by applying the same transform to the original ticks.
    original_ticks = [0, 255]
    transformed_ticks = [tick * compression_factor + offset for tick in original_ticks]
    plt.yticks(transformed_ticks, [str(t) for t in original_ticks], fontsize=24)
    plt.ylabel("Received Brightness \n Value (0-255)", fontsize=24)

    # 9) Adjust the spines: hide the top/right and restrict the left spine to the compressed region.
    plt.grid(False)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_bounds(time_axis[0], time_axis[-1])
    ax.spines['left'].set_bounds(offset, offset + new_range)

    plt.tight_layout()
    plt.show()

def plot_colour_frame_comparison(frame_timestamps_and_colours_csv_path, rgb_csv_path, corrected_rgb_csv_path, key, colour):
    """
    Plots a comparison of transmitted, received, and corrected values for a single colour channel.
    
    Parameters:
      frame_timestamps_and_colours_csv_path (str):
          Path to the CSV file produced by frame_colour_matching. This CSV has columns:
          "frame_number", "timestamp", "R", "G", "B", "matched_log_timestamp".
      rgb_csv_path (str):
          Path to a 0-indexed CSV (with no header) in the form:
          r1,g1,b1,r2,g2,b2,..., where each set of three columns corresponds to one key.
      corrected_rgb_csv_path (str):
          Path to a CSV formatted identically to rgb_csv_path but with corrected values.
      key (int):
          The key number to extract. For example, key=2 corresponds to the 4th, 5th, and 6th columns.
      colour (str):
          A single character specifying the colour channel to plot, e.g. 'R', 'G', or 'B'.
    
    Operation:
      - Reads the transmitted CSV.
      - Reads the measured rgb_csv and corrected_rgb_csv, and extracts only the rows whose index equals the
        "frame_number" from the transmitted CSV.
      - For each transmitted frame, extracts the transmitted value (from the transmitted CSV), the
        received value (from rgb_csv), and the corrected value (from corrected_rgb_csv) for the specified key and colour.
      - Plots these three series on the same graph with "Video Frame" on the x-axis and a y-axis from 0 to 255.
      - Uses MATLAB default colors:
            * Transmitted: solid line, blue (#0072BD)
            * Received: dashed line, orange (#D95319)
            * Corrected: dotted line, yellow (#EDB120)
      - A legend is added with appropriate labels.
    """
    # Mapping from colour letter to offset within a key's triplet.
    colour_offset = {'R': 0, 'G': 1, 'B': 2}
    if colour not in colour_offset:
        raise ValueError(f"Unknown colour '{colour}'. Expected one of 'R', 'G', 'B'.")
    
    # Read transmitted CSV.
    transmitted_data = []
    with open(frame_timestamps_and_colours_csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                frame_number = int(row["frame_number"])
            except ValueError:
                continue
            transmitted_data.append({
                "frame_number": frame_number,
                "timestamp": row["timestamp"],
                "R": row.get("R", ""),
                "G": row.get("G", ""),
                "B": row.get("B", "")
            })
    
    # Read measured RGB CSVs (no header)
    def read_no_header_csv(path):
        data = []
        with open(path, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
        return data

    rgb_data = read_no_header_csv(rgb_csv_path)
    corrected_data = read_no_header_csv(corrected_rgb_csv_path)
    
    # Determine the column index for the specified key and colour.
    base_index = (key - 1) * 3
    requested_index = base_index + colour_offset[colour]
    
    # Build a series dictionary.
    series = {"frames": [], "transmitted": [], "received": [], "corrected": []}
    
    for row in transmitted_data:
        frame_number = row["frame_number"]
        if frame_number < 0 or frame_number >= len(rgb_data) or frame_number >= len(corrected_data):
            continue
        
        try:
            transmitted_val = float(row[colour])
        except (ValueError, TypeError):
            transmitted_val = None

        try:
            received_val = float(rgb_data[frame_number][requested_index])
        except (IndexError, ValueError):
            received_val = None

        try:
            corrected_val = float(corrected_data[frame_number][requested_index])
        except (IndexError, ValueError):
            corrected_val = None
        
        if transmitted_val is not None:
            series["frames"].append(frame_number)
            series["transmitted"].append(transmitted_val)
            series["received"].append(received_val)
            series["corrected"].append(corrected_val)
    
    # Plotting using MATLAB default colors.
    plt.figure(facecolor='white')
    if series["frames"]:
        plt.plot(series["frames"], series["transmitted"], linestyle='-', color='#0072BD', 
                 label=f"{colour} value transmitted")
        plt.plot(series["frames"], series["received"], linestyle='--', color='#D95319', 
                 label=f"{colour} value received")
        plt.plot(series["frames"], series["corrected"], linestyle=':', color='#EDB120', 
                 label=f"{colour} value corrected")
    else:
        print("No data available for plotting.")
        return

    plt.xlabel("Video Frame")
    plt.ylabel("Colour Value (0-255)")
    plt.ylim(0, 255)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()

# Example usage:

# keys = tuple(range(1,110))
# colours = ('R','G','B')

# for key in keys:
#     for colour in colours: 
#         print(f'KEY: {key}, COLOUR: {colour}')
#         plot_colour_frame_comparison("files/spreadsheets/frame_timestamps_and_colours.csv",
#                                     'files/spreadsheets/s5_rgb_normalised.csv',
#                                     "files/spreadsheets/s6_rgb_corrected.csv",
#                                     key=key,
#                                     colour=colour)

# For Synchronous Communication: ##

signal_csv_path = 'files/key_light_levels/light_levels_CLK.csv'
display_binary_reading_with_markers(signal_csv_path)

signal_csv_path = 'files/key_light_levels/light_levels_SGL.csv'
display_binary_reading_with_markers(signal_csv_path)

key = 3

while key <= 108:
    print(f'key{key}')
    signal_csv_path = f'files/key_light_levels/light_levels_key_{key}.csv'
    display_binary_reading_with_markers(signal_csv_path)
    key += 1

## For Analogue Communication: ##

# csv_path = "files\spreadsheets\s5_rgb_normalised.csv"

# ns = tuple(range(0, 109*3))

# for n in ns:
#     display_ASK_reading(csv_path, column=n, framerate=60)