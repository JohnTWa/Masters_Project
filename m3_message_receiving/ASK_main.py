from _SETUP_ import set_directory
set_directory()

from common.file_handling import append_to_txt
from common.reset import reset
from m3_message_receiving.edge_detection import detect_edges_with_orig_index
from common.hamming_code import hamming_decode
from common.ASCII import binary_to_ascii
from m3_message_receiving.ASK_synchronous.determine_states import determine_states

## Define paths ##

key_levels_and_events_folder = 'files/key_light_levels'
rgb_csv_path = 'files/spreadsheets/s4_rgb_averages.csv'
CLK_csv_path = key_levels_and_events_folder + '/light_levels_CLK.csv'
SGL_csv_path = key_levels_and_events_folder + '/light_levels_SGL.csv'
binary_csv_path = 'files/spreadsheets/s8_binary.csv'
output_text_path = 'files/t2_received_text.txt'

## Define signal parameters ##

codeword_bits = 11
frequency = 10 # transmission frequency in Hz
camera_sample_rate = 60 # camera framerate in fps

## Calculate parameters ##

frame_bits = codeword_bits

## Reset Files ##

reset(binary_csv_path, output_text_path, key_levels_and_events_folder)

## Read CLK and SGL Keys ##

CLK = detect_edges_with_orig_index(rgb_csv_path, 0, CLK_csv_path, threshold_fraction=0.2)
SGL = detect_edges_with_orig_index(rgb_csv_path, 3, SGL_csv_path, threshold_fraction=0.2)
frame_bounds = list(zip(SGL[::2], SGL[1::2])) # 'frame' here pertaining to the transmission frame not video frame
print(f'Clock Flips: {len(CLK)}, Signal Flips: {len(SGL)}, Frames: {len(frame_bounds)}')
print(f'Bits per Frame: expected-{frame_bits}, detected-{len(CLK)/len(frame_bounds)}')

## For Each transmitting key: ##

key = 3 # third key is first data key
while key <= 109:

    colour_n = (key-1)%3
    column = (key-1)*3 + colour_n
    colour_dictionary = {0:'R', 1:'G', 2:'B'}
    colour = colour_dictionary[colour_n]
    print(f'Key {key}, Colour {colour}, Column {column}')
    levels_and_events_csv_path = key_levels_and_events_folder + f'/light_levels_key_{key}.csv'
    _ = detect_edges_with_orig_index(rgb_csv_path, column-1, levels_and_events_csv_path, threshold_fraction=0.1)

    print(f'|Reading key {key}, column {column}')

    signal_number = 1
    ## For each frame ##
    for frame_bound in frame_bounds:

        print(f'||Reading signal {signal_number}, between rows {frame_bound}')
        start, end = frame_bound
        print(f'||Start: {start}, End: {end}')
        codeword = determine_states(levels_and_events_csv_path, CLK, frame_bound)
        print(f'||Codeword: {codeword}')
        payload = hamming_decode(codeword)
        character = binary_to_ascii(payload)
        print(f'||Character: {character}')
        append_to_txt(output_text_path, signal_number, character)

        signal_number += 1
    
    key += 1