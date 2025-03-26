from common.file_handling import append_to_txt
from common.reset import reset
from m3_message_receiving.edge_detection import detect_edges
from common.hamming_code import hamming_decode
from common.ASCII import binary_to_ascii
from receiving_asynchronous.frame_bounds import determine_frame_bounds
from m3_message_receiving.receiving_asynchronous.repeat_detection import mark_bit_repeats
from m3_message_receiving.receiving_asynchronous.signal_reading import read_signal

## Define file paths ##

signal_csv_path = 'files/signal_IDs.csv'
rgb_csv_path = 'files/s3_rgb_averages.csv'
key_readings_path = 'files/key_readings'
binary_csv_path = 'files/s5_binary.csv'
output_text_path = 'files/t2_received_text.txt'

## Define signal parameters ##

start_bits = 1
codeword_bits = 12
end_bits = 1
frequency = 10
framerate = 60
tolerance = 2
consideration_bounds = (1, 2190)

## Calculate parameters ##

idle_bits = codeword_bits+1
signal_bits = (start_bits + codeword_bits + end_bits)
bit_rows = framerate/frequency
idle_rows = round(0.9*idle_bits*bit_rows)

# Printing Diagnostic signals
print(f'Reading at frequency {frequency} Hz, with '
    f'{round(bit_rows, 2)} rows for each bit, '
    f'{idle_rows} row idle zones between signals, ')

## Reset Files ##

reset(binary_csv_path, output_text_path, key_readings_path)

## For Each transmitting key: ##

column = 1
while column < 327:

    key = round((column+1)/3)
    edges_csv_path = key_readings_path + f'/readings_key_{key}.csv'
    detect_edges(rgb_csv_path, column-1, edges_csv_path, threshold_fraction=0.1)

    print(f'|Reading key {key}, column {column}')

    # Determining Frame Bounds
    signal_bounds, transmissions = determine_frame_bounds(edges_csv_path, idle_rows, 0, consideration_bounds, True)

    # Initialising
    signal_number = 1 
    ## For each signal ##
    for signal_bound in signal_bounds:

        print(f'||Reading signal {signal_number}, between rows {signal_bound}')
        mark_bit_repeats(edges_csv_path, bit_rows, tolerance, signal_bound)
        codeword = read_signal(edges_csv_path, signal_bound, start_bits, end_bits, 11, True)
        payload = hamming_decode(codeword)
        character = binary_to_ascii(payload)
        append_to_txt(output_text_path, signal_number, character)

        signal_number += 1
    
    column += 4