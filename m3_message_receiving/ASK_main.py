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
rgb_csv_path = 'files/s3_rgb_averages.csv'
CLK_csv_path = key_levels_and_events_folder + '/light_levels_CLK.csv'
SGL_csv_path = key_levels_and_events_folder + '/light_levels_SGL.csv'
binary_csv_path = 'files/s5_binary.csv'
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

column = 7 # Start at column 7, which is key 3, colour R. 
while column < 333:

    key = 1 + round(column/3) # Calculate key from column number
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
    
    column += 4 # Move to next key, next colour: for example, key 4, colour G

# Currently, frames are sent on different colours for each data transmitting key, in the format: 
    # key1 R, key2 G, key3 B, key5 R, key6 G, key7 B, ...
    # Notice that every 4th key is skipped, as it is not used for transmission.