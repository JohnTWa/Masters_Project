import csv
from collections import defaultdict
import numpy as np

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