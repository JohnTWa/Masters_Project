from _SETUP_ import set_directory
set_directory()

import time
from common.file_handling import csv_to_list, adjust_for_Corsair_logo
from common.hamming_code import hamming_encode
from common.keyboard_interface import keyboard_setup, set_colour_timed
from m1_transmitting.modulation.formatting import rs232_modified_format
from common.ASCII import file_to_ascii_binary, list_splitting, pad_signals, insert_padding
from m1_transmitting.modulation.ASK_modulation import send_binary_signals_alternating_RGB

## Define transmission parameters ##

key_ids_path = 'files/spreadsheets/s1_key_IDs.csv'
transmission_text_path = 'files/t1_transmission_text.txt'
pause_time = 1
frequency = 10
framerate = 60

## Determine key IDs

key_IDs = csv_to_list(key_ids_path)
key_IDs = adjust_for_Corsair_logo(key_IDs)
number_of_keys = len(key_IDs)

## Encode and Format the data ##

binary_data = file_to_ascii_binary(transmission_text_path)  

signals = []
for data in binary_data:

    codeword = hamming_encode(data)
    idle_bits = len(codeword)+1
    signal = rs232_modified_format(codeword, idle_bits)
    signals.append(signal)

signal_bits = len(signals[0])
signal_sets = list_splitting(signals, number_of_keys)
number_of_transmissions = len(signal_sets)
print(signal_sets)

## Calculate transmission time ## 

bit_length = 1/frequency
signal_time = signal_bits*bit_length
total_transmission_time = round(number_of_transmissions * signal_time) # in whole seconds

print(f'Time (s): {total_transmission_time}, '
      f'(mins): {total_transmission_time/60}, '
      f'(hours): {total_transmission_time/3600}')

## Transmit the signals ##

sdk, device_id, CorsairLedColor = keyboard_setup()
setup_items = [sdk, device_id, CorsairLedColor]
time.sleep(0.1)
set_colour_timed(setup_items, 
                 key_IDs, 
                 colour=(255,0,0), # RED
                 time_length=1.0, 
                 verbose=1
)

for signal_set in signal_sets:
    send_binary_signals_alternating_RGB(setup_items, 
                                        signal_set, 
                                        key_IDs, 
                                        frequency)