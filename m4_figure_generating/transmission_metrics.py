import numpy as np
import matplotlib.pyplot as plt
import csv
from collections import defaultdict
import plotly.graph_objects as go

def statistical_analysis(
    grouped_binary_csv_path, 
    f_index, 
    bin_index, 
    correct_message, 
    transmissions_at_each_f, 
    frequencies
):
    """
    Performs statistical analysis on a pre-grouped CSV file where the first column contains frequency values.

    Parameters:
    - grouped_binary_csv_path (str): Path to the input grouped CSV file.
    - f_index (int): Column index for frequency values.
    - bin_index (int): Column index for binary messages.
    - correct_message (str): The correct binary message string to compare.
    - transmissions_at_each_f (int): Number of transmissions expected at each frequency.
    - frequencies (list): List of expected frequencies.

    Returns:
    - list of tuples: Each tuple contains (frequency, reception_rate, success_rate, bit_error_rate, bit_error_of_successes).
    """
    correct_message_length = len(correct_message)
    results = []
    frequency_groups = defaultdict(list)

    # Read the grouped CSV and organize rows by frequency
    with open(grouped_binary_csv_path, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

        for row in rows:
            try:
                frequency = float(row[f_index])
                frequency_groups[frequency].append(row)
            except (ValueError, IndexError):
                continue  # Skip rows with invalid frequency values

    # Perform analysis for each expected frequency
    for freq in frequencies:
        group = frequency_groups.get(freq, [])
        num_received = len(group)
        reception_rate = num_received / transmissions_at_each_f if transmissions_at_each_f > 0 else 0

        # Calculate success rate
        num_correct = sum(1 for row in group if row[bin_index].strip() == correct_message)
        success_rate = num_correct / transmissions_at_each_f if transmissions_at_each_f > 0 else 0

        # Calculate bit error rate
        total_bit_errors = 0
        bit_error_of_successes = None
        total_bit_error_across_received = 0

        for row in group:
            binary_message = row[bin_index].strip()
            # Count bit errors for each received message
            bit_errors = sum(1 for m1, m2 in zip(binary_message, correct_message) if m1 != m2)
            total_bit_errors += bit_errors
            total_bit_error_across_received += bit_errors / correct_message_length

        # Normalize bit error of successes by received messages
        if num_received > 0:
            bit_error_of_successes = total_bit_error_across_received / num_received
        else:
            bit_error_of_successes = None

        # Bit error rate including messages not received
        total_bits = transmissions_at_each_f * correct_message_length
        missed_transmissions_bit_errors = (transmissions_at_each_f - num_received) * correct_message_length
        total_bit_error_rate = (total_bit_errors + missed_transmissions_bit_errors) / total_bits if total_bits > 0 else 0

        # Save results for this frequency
        results.append((freq, reception_rate, success_rate, total_bit_error_rate, bit_error_of_successes))

    return results

# Example usage:
# grouped_binary_csv_path = "grouped_binary_messages.csv"
# f_index = 0  # Frequency column index
# bin_index = 3  # Binary message column index
# correct_message = "10110011"
# transmissions_at_each_f = 10
# frequencies = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
# results = statistical_analysis(grouped_binary_csv_path, f_index, bin_index, correct_message, transmissions_at_each_f, frequencies)

# for result in results:
#     print(f"Frequency: {result[0]} Hz")
#     print(f"  Reception Rate: {result[1]:.2f}")
#     print(f"  Success Rate: {result[2]:.2f}")
#     print(f"  Total Bit Error Rate: {result[3]:.4f}")
#     print(f"  Bit Error Rate of Successes: {result[4]:.4f}" if result[4] is not None else "  Bit Error Rate of Successes: N/A")

def display_statistics_together(statistics, metric_names=None):
    """
    Plots a graph of the first column on the x-axis (frequency) and other columns on the y-axis,
    each on its own scale of 0 to the maximum value. Negative values are plotted below the x-axis.
    The x values are always annotated as whole numbers. Bit Error of Received Messages is plotted as points.

    Parameters:
    - statistics (list of tuples): Each tuple contains a frequency and corresponding metrics.
    - metric_names (list of str): Names of the metrics for the legend (optional). Defaults to standard metric names.
    """
    statistics = np.array(statistics)  # Convert to numpy array for easier handling
    x = statistics[:, 0]  # First column (e.g., frequencies)
    y_metrics = statistics[:, 1:]  # Remaining columns (metrics)
    
    # Default metric names if not provided
    if metric_names is None:
        metric_names = ["Reception Rate", "Success Rate", "Total Bit Error Rate", "Bit Error of Received Messages"]
    
    plt.figure(figsize=(10, 6))
    for i in range(y_metrics.shape[1]):
        y = y_metrics[:, i]
        if metric_names[i].lower() == "Bit Error of Successful Transmissions":
            # Plot bit error of successes as points
            plt.scatter(x, y, label=metric_names[i], marker='o')
        else:
            y_scaled = y / np.max(np.abs(y)) if np.max(np.abs(y)) > 0 else y  # Scale to 0-1 range
            plt.plot(x, y_scaled * np.max(y), label=metric_names[i])

    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add x-axis at 0
    plt.title("Statistics Together")
    plt.xlabel("Frequency")
    plt.ylabel("Metrics (scaled)")
    plt.legend()
    plt.grid(True)
    plt.xticks(np.arange(np.floor(np.min(x)), np.ceil(np.max(x)) + 1, 1))  # Whole number x ticks
    plt.show()


def display_statistics_separately(statistics, metric_names=None):
    """
    Plots each metric in a separate graph in a grid, with the first column on the x-axis (frequency).
    Bit Error of Successes is plotted as points. Assumes dynamic adjustment for any number of metrics.

    Parameters:
    - statistics (list of tuples): Each tuple contains a frequency and corresponding metrics.
    - metric_names (list of str): Names of the metrics for the titles and legends (optional). Defaults to standard metric names.
    """
    statistics = np.array(statistics)  # Convert to numpy array for easier handling
    x = statistics[:, 0]  # First column (e.g., frequencies)
    y_metrics = statistics[:, 1:]  # Remaining columns (metrics)
    num_metrics = y_metrics.shape[1]
    
    # Default metric names if not provided
    if metric_names is None:
        metric_names = ["Reception Rate", "Success Rate", "Total Bit Error Rate", "Bit Error of Successes"]
    
    # Determine grid size for plotting
    cols = 2
    rows = (num_metrics + 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(12, rows * 4))
    axes = axes.flatten()  # Flatten for easier indexing
    
    for i in range(num_metrics):
        y = y_metrics[:, i]
        ax = axes[i]
        if metric_names[i].lower() == "bit error of successes":
            # Plot bit error of successes as points
            ax.scatter(x, y, label=metric_names[i], marker='o')
        else:
            ax.plot(x, y, label=metric_names[i])
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add x-axis at 0
        ax.set_title(metric_names[i])
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)
        ax.set_xticks(np.arange(np.floor(np.min(x)), np.ceil(np.max(x)) + 1, 1))  # Whole number x ticks
    
    # Hide unused subplots
    for j in range(num_metrics, len(axes)):
        axes[j].set_visible(False)
    
    plt.tight_layout()
    plt.show()

def plot_bit_error_rate(statistics):
    """
    Plots the Total Bit Error Rate against Frequency.

    Parameters:
    - statistics (list of tuples): Each tuple contains:
        (frequency, reception_rate, success_rate, total_bit_error_rate, bit_error_of_successes)

    Behavior:
    - Extracts frequency and total_bit_error_rate from statistics.
    - Plots Frequency on the x-axis and Total Bit Error Rate on the y-axis.
    - Displays the plot with appropriate labels and title.
    """
    if not statistics:
        print("No statistics data provided.")
        return

    # Extract frequencies and total_bit_error_rates
    frequencies = []
    total_bit_error_rates = []

    for entry in statistics:
        try:
            freq = float(entry[0])
            bit_error_rate = float(entry[3])
            frequencies.append(freq)
            total_bit_error_rates.append(bit_error_rate)
        except (IndexError, ValueError) as e:
            print(f"Skipping entry due to error: {e}")
            continue

    if not frequencies or not total_bit_error_rates:
        print("No valid frequency or bit error rate data to plot.")
        return

    # Sort the data by frequency for a coherent plot
    sorted_data = sorted(zip(frequencies, total_bit_error_rates), key=lambda x: x[0])
    sorted_frequencies, sorted_bit_error_rates = zip(*sorted_data)

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_frequencies, sorted_bit_error_rates, marker='none', color='black', linestyle='-')

    # Set plot labels and title
    plt.xlabel("Frequency (Hz)", fontsize=12)
    plt.ylabel("Total Bit Error Rate", fontsize=12)
    plt.title("Total Bit Error Rate vs Frequency", fontsize=14)

    # Enable grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Optionally, adjust x-ticks to be whole numbers if frequencies are integers
    if all(freq.is_integer() for freq in sorted_frequencies):
        plt.xticks(sorted_frequencies)

    # Display the plot
    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def plot_bit_error_rate_multiple(statistics_list, labels, colors=None, line_styles=None):
    """
    Plots multiple Total Bit Error Rates against Frequency on the same graph.

    Parameters:
    - statistics_list (list of lists): Each sublist contains tuples of statistics for a file.
    - labels (list of str): Labels for each BER curve corresponding to the statistics_list.
    - colors (list of str, optional): List of colors for each BER curve. Defaults to Matplotlib's color cycle.
    - line_styles (list of str, optional): List of line styles for each BER curve. Defaults to solid lines.

    Behavior:
    - Each BER curve is plotted with its corresponding label, color, and line style.
    - A legend distinguishes between different tolerance levels.
    - The plot title is set to "Total Bit Error Rate vs Frequency".
    - Y-axis boundaries are set between 0 and 1 with intervals of 0.1.
    - A horizontal red line labeled "Random Guessing" is added at y=0.5.
    - No grid is displayed.
    """
    if not statistics_list or not labels:
        print("Error: statistics_list and labels must be provided and non-empty.")
        return
    
    if len(statistics_list) != len(labels):
        print("Error: The length of statistics_list and labels must be the same.")
        return

    # Handle default colors if not provided
    if colors is None:
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = [color_cycle[i % len(color_cycle)] for i in range(len(statistics_list))]
    else:
        if len(colors) < len(statistics_list):
            print("Warning: Not enough colors provided. Using default colors for remaining curves.")
            default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            colors += [default_colors[i % len(default_colors)] for i in range(len(statistics_list) - len(colors))]

    # Handle default line styles if not provided
    if line_styles is None:
        line_styles = ['-'] * len(statistics_list)  # Solid lines by default
    else:
        if len(line_styles) < len(statistics_list):
            print("Warning: Not enough line styles provided. Using solid lines for remaining curves.")
            line_styles += ['-'] * (len(statistics_list) - len(line_styles))

    plt.figure(figsize=(12, 8))

    for idx, (statistics, label) in enumerate(zip(statistics_list, labels)):
        # Extract frequencies and total_bit_error_rates
        frequencies = []
        total_bit_error_rates = []

        for entry in statistics:
            try:
                freq = float(entry[0])
                ber = float(entry[3])
                frequencies.append(freq)
                total_bit_error_rates.append(ber)
            except (IndexError, ValueError) as e:
                print(f"Skipping entry due to error: {e}")
                continue

        if not frequencies or not total_bit_error_rates:
            print(f"Warning: No valid data to plot for label '{label}'.")
            continue

        # Sort the data by frequency for a coherent plot
        sorted_data = sorted(zip(frequencies, total_bit_error_rates), key=lambda x: x[0])
        sorted_frequencies, sorted_bit_error_rates = zip(*sorted_data)

        # Select color and line style
        color = colors[idx]
        line_style = line_styles[idx]

        # Plot each BER curve with specified color and line style, no markers
        plt.plot(
            sorted_frequencies,
            sorted_bit_error_rates,
            linestyle=line_style,
            color=color,
            label=label
        )

    # Set plot labels and updated title
    plt.xlabel("Frequency (Hz)", fontsize=14)
    plt.ylabel("Total Bit Error Rate", fontsize=14)
    plt.title("Total Bit Error Rate vs Frequency", fontsize=16)

    # Set y-axis boundaries between 0 and 1
    plt.ylim(0, 1)

    # Set y-axis ticks at intervals of 0.1
    plt.yticks([i/10 for i in range(0, 11, 1)])  # Generates [0.0, 0.1, 0.2, ..., 1.0]

    # Add a horizontal red line at y=0.5 labeled "Random Guessing"
    plt.axhline(y=0.5, color='red', linestyle='-.', linewidth=1.5, label="Random Guessing")

    # Legend without title
    plt.legend()

    # Optionally, adjust x-ticks to be whole numbers if frequencies are integers
    # Flatten all frequencies to check if all are integers
    all_frequencies = [freq for statistics in statistics_list for (freq, _, _, _, _) in statistics]
    if all(freq == int(freq) for freq in all_frequencies):
        unique_frequencies = sorted(set(all_frequencies))
        plt.xticks(unique_frequencies)

    # Display the plot
    plt.tight_layout()
    plt.show()

binary_folder = 'files/binary_files'
statistics = []
labels = []
colours = ['black', 'black', 'orange', 'orange', 'green', 'green', 'blue', 'blue']
line_styles = []
Keys = [1,40,80,120]
iterations_at_each_f = [40,20,20,20]
frequencies = [list(range(5,30))] + [list(range(10,30))] * 3
print(frequencies)

n = 0
for Key in Keys:
    T = 1
    while T <= 2:
        binary_csv = binary_folder + f'/binary_{Key}Key_T{T}.csv'
        statistics.append(statistical_analysis(binary_csv , 0, 1, '10110001', iterations_at_each_f[n], frequencies[n]))
        labels.append(f'{min(Key, 109)} Keys, Tolerance = {T}')
        lightness = 8
        blueness = n * 2
        line_styles.append('-'*T)
        T+=1
    n += 1

plot_bit_error_rate_multiple(statistics, labels, colours, line_styles)