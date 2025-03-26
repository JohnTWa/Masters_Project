from _SETUP_ import set_directory
set_directory()

from common.file_handling import csv_to_tuple
from common.hamming_code import hamming_encode
from common.ASCII import file_to_ascii_binary, list_splitting, pad_signals, insert_padding
from m1_transmitting.modulation.ASK_modulation import send_binary_signal, send_binary_signals_with_CLK_and_SGL

## Define transmission parameters ##

key_ids_path = 'files/key_IDs.csv'
data_ids_path = 'files/data_IDs.csv'
transmission_text_path = 'files/t1_transmission_text.txt'
pause_time = 1
frequency = 10
framerate = 60
idle_bits = 1

## Determine key IDs ##

CLK_IDs = [196609, 196610]
SGL_IDs = [1,]
key_IDs = csv_to_tuple(key_ids_path)
data_IDs = csv_to_tuple(data_ids_path)
number_of_keys = len(data_IDs)

## Encode and Format the data ##

binary_data = file_to_ascii_binary(transmission_text_path)  

signals = []
for data in binary_data:

    codeword = hamming_encode(data)
    signals.append(codeword)

signal_bits = len(signals[0])
signal_sets = list_splitting(signals, round(number_of_keys*3/4))
number_of_transmissions = len(signal_sets)

## Calculate transmission time ## 

bit_length = 1/frequency
signal_time = (signal_bits+idle_bits*bit_length)
total_transmission_time = round(number_of_transmissions * signal_time) # in whole seconds

print(f'Time (s): {total_transmission_time}, '
      f'(mins): {total_transmission_time/60}, '
      f'(hours): {total_transmission_time/3600}')

## Transmit the signals ##
 
send_binary_signal('0', key_IDs, 1/2)
send_binary_signal('0', key_IDs, 1/4)

for signal_set in signal_sets:
    padded_signals = pad_signals(signal_set, '0'*signal_bits, 3)
    if len(padded_signals) > 75*3-3:
        padded_signals = insert_padding(padded_signals, '0'*signal_bits, 3, 75*3-3)

    send_binary_signal('0', key_IDs, frequency)
    send_binary_signals_with_CLK_and_SGL(
        binary_signals=padded_signals,
        data_ids=data_IDs,
        CLK_ids=CLK_IDs,
        SGL_ids=SGL_IDs,
        frequency=frequency        
        )
    send_binary_signal('0', key_IDs, frequency)

send_binary_signal('0', key_IDs, 1/4)