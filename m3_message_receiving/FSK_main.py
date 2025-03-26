from _SETUP_ import set_directory
set_directory()

import heapq

from m3_message_receiving.FSK.zero_crossing import zero_crossing_count

## Define Filepaths ##

rgb_csv_path = 'files/s3_rgb_averages.csv'

## Define signal parameters ##

bits_per_frame = 8
T_bit = 2 # bit length (s)
frequency_set = (1, 2)
camera_sample_rate = 60 # camera framerate in fps
signal_start_row = 0
samples_per_bit = camera_sample_rate * T_bit

## Demodulate Frame ##

frame = ''
for bit in list(range(bits_per_frame)):

    bit_start_row = signal_start_row + bit * samples_per_bit
    next_bit_start_row = bit_start_row + samples_per_bit
    print(f'Bit {bit} Rows: {bit_start_row} to {next_bit_start_row-1}')

    zero_crossings = zero_crossing_count(rgb_csv_path, 
                                    column=0, 
                                    consideration_bounds=(bit_start_row, next_bit_start_row-10), 
                                    sampling_rate=camera_sample_rate
                                    )
    
    frequency_estimate = zero_crossings / (2 * T_bit)
    most_likely_frequency = heapq.nsmallest(1, frequency_set, key=lambda x: abs(x-frequency_estimate))[0]
    bit_value = frequency_set.index(most_likely_frequency)
    frame = frame + str(bit_value)
    print(f'Bit {bit} Frequency: {frequency_estimate}, Closest to f = {most_likely_frequency} Hz, Bit Value = {bit_value})')

print(f'Frame: {frame}')