from common.reset import reset, delete_columns, clear_repeats
from m3_message_receiving.edge_detection import detect_edges
from common.statistical_analysis import statistical_analysis
from c_message_decoding.pause_location import determine_pause_bounds
from c_message_decoding.rs232m.message_location import determine_message_bounds
from c_message_decoding.repeat_detection import mark_bit_repeats
from c_message_decoding.message_reading import decode_message, write_to_csv_new_row

## Define message parameters ##

idle_bits = 8
start_bits = 1
message_bits = 7
end_bits = 1
frequency = 10
transmissions = 11

framerate = 60

## Calculate key parameters ##

signal_bits = (start_bits + message_bits + end_bits)

## Define file paths ##

rgb_csv_path = 'files/s3_rgb_averages.csv'
signal_csv_path = 'files/s4_signal.csv'
binary_csv_path = 'files/s5_binary.csv'
grouped_binary_csv_path = 'files/s6_grouped_binary.csv'

## Run the Process ##

reset(binary_csv_path, grouped_binary_csv_path)
delete_columns(signal_csv_path, 3)
clear_repeats(signal_csv_path)
detect_edges(rgb_csv_path, 0, signal_csv_path, threshold_fraction=0.1, start_row=None, end_row=None)


# Define Parameters for This Frequency
bit_rows = framerate/frequency
idle_rows = round(0.9*idle_bits*bit_rows)
tolerance = 0 
consideration_bounds = (1, 1200)

# Printing Diagnostic Messages
print(f'Reading at frequency {frequency} Hz, with '
        f'{round(bit_rows, 2)} rows for each bit, '
        f'{idle_rows} row idle zones between signals, ')

# Determining Signal Bounds
message_bounds, transmissions = determine_message_bounds(signal_csv_path, idle_rows, 0, consideration_bounds, True)
print(message_bounds)

signal = 1 
## For each message ##
for message_bound in message_bounds:

    print(f'Reading message {signal}, between rows {message_bound}')
    mark_bit_repeats(signal_csv_path, bit_rows, tolerance, message_bound)
    message = decode_message(signal_csv_path, message_bound, 1, 0, 8, True)
    write_to_csv_new_row(binary_csv_path, message)

    signal += 1