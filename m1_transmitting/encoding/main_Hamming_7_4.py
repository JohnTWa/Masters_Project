import time
from common.file_handling import csv_to_tuple
from common.hamming_code import hamming_encode
from m1_transmitting.formatters.asynchronous_formatting import rs232_modified_format
from common.ASCII import file_to_ascii_binary, list_splitting, pad_signals, insert_padding
from m1_transmitting.modulating.ASK_modulation import send_binary_signal, send_binary_signals

## Define transmission parameters ##

key_ids_path = 'files/key_IDs.csv'
transmission_text_path = 'files/t1_transmission_text.txt'
pause_time = 1
frequency = 10
framerate = 60

## Determine key IDs

IDs = csv_to_tuple(key_ids_path)
number_of_keys = len(IDs)

## Encode and Format the data ##

binary_data = file_to_ascii_binary(transmission_text_path) 
idle_bits = len(binary_data[0])+1

signals = []
for data in binary_data:

    data1 = '0' + data[:3]
    codeword1 = hamming_encode(data1)
    signal1 = rs232_modified_format(codeword1, idle_bits)
    signals.append(signal1)

    data2 = data[3:]
    codeword2 = hamming_encode(data2)
    signal2 = rs232_modified_format(codeword2, idle_bits)
    signals.append(signal2)

## Calculate additional transmission Parameters ##

signal_bits = len(signals[0])
signal_sets = list_splitting(signals, round(number_of_keys*3/4))
number_of_transmissions = len(signal_sets)

## Calculate transmission time ## 

bit_length = 1/frequency
signal_time = signal_bits*bit_length
total_transmission_time = round(number_of_transmissions * signal_time) # in whole seconds

print(f'Time (s): {total_transmission_time}, '
      f'(mins): {total_transmission_time/60}, '
      f'(hours): {total_transmission_time/3600}')

## Transmit the signals ##
 
send_binary_signal('0', IDs, 0.5)
send_binary_signal('0', IDs, 1/4)

for signal_set in signal_sets:
    padded_signals = pad_signals(signal_set, '0'*signal_bits, 3)
    padded_signals = insert_padding(padded_signals, '0'*signal_bits, 3, 75*3-3)
    print(len(padded_signals))
    send_binary_signals(padded_signals, IDs, frequency)
    print(padded_signals)

send_binary_signal('0', IDs, 1/4)