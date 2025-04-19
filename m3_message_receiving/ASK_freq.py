from _SETUP_ import set_directory
set_directory()

from common.file_handling import append_to_txt, write_to_csv_new_row
from common.reset import reset
from m3_message_receiving.edge_detection import detect_edges_with_orig_index
from common.hamming_code import hamming_decode
from common.ASCII import binary_to_ascii
from m3_message_receiving.ASK_synchronous.determine_states import determine_states
from m3_message_receiving.ASK_asynchronous.pause_location import determine_pause_bounds
import m4_figure_generating.BER_vs_f as BER_vs_f

# Packages
import logging
import pandas as pd

## Define paths ##

log_file_path = 'files/logs/ASK_frequency_testing.log'
key_levels_and_events_folder = 'files/key_light_levels'
rgb_csv_path = 'files/spreadsheets/s5_rgb_normalised.csv'
CLK_csv_path = key_levels_and_events_folder + '/light_levels_CLK.csv'
SGL_csv_path = key_levels_and_events_folder + '/light_levels_SGL.csv'
binary_csv_path = 'files/spreadsheets/s8_binary.csv'
BER_vs_f_CSV = 'files/spreadsheets/BER_vs_f/synch.csv'

# Configure the logger to write to a file, e.g., 'app.log'
logging.basicConfig(
    filename=log_file_path,        # log file name
    filemode='w',              # append mode; use 'w' to overwrite each time
    format='%(asctime)s \t %(levelname)s \t %(message)s',
    level=logging.INFO         # logging level; adjust as needed
)
logger = logging.getLogger(__name__)

## Define signal parameters ##

expected_payload = '10110001'
frequencies = list(range(10, 31)) # Hz
camera_sample_rate = 60 # camera framerate in fps
frame_bits = len(expected_payload)
pause_time = 0.8 # seconds
frames_per_frequency = 20

## Reset Files ##

reset(binary_csv_path, BER_vs_f_CSV, key_levels_and_events_folder)
write_to_csv_new_row(binary_csv_path, 'Frequency (Hz)', 'Payload')
write_to_csv_new_row(BER_vs_f_CSV, 'Frequency (Hz)', 'BER')

## Read CLK and SGL Keys ##

CLK = detect_edges_with_orig_index(rgb_csv_path, 0, CLK_csv_path, threshold_fraction=0.2)
SGL = detect_edges_with_orig_index(rgb_csv_path, 3, SGL_csv_path, threshold_fraction=0.1)
frame_bounds = list(zip(SGL[::2], SGL[1::2])) # 'frame' here pertaining to the transmission frame not video frame
print(f'Clock Flips: {len(CLK)}, Signal Flips: {len(SGL)}, Frames: {len(frame_bounds)}')
print(f'Bits per Frame: expected-{frame_bits}, detected-{len(CLK)/len(frame_bounds)}')

## For First Data Key: ##

key = 3  # third key is first data key
column = 6
logger.info(f'Key {key}, Colour 'R', Column {column}')
levels_and_events_csv_path = key_levels_and_events_folder + f'/light_levels_key_{key}.csv'
_ = detect_edges_with_orig_index(rgb_csv_path, column, levels_and_events_csv_path, threshold_fraction=0.1)

## Determining Frequency Boundaries ##

frame_bounds_frequency_sorted = []
pause_rows = int(pause_time * camera_sample_rate)
pause_bounds = determine_pause_bounds(CLK_csv_path, pause_rows=pause_rows, mark=False)
logger.info(f'Number of pauses: {len(pause_bounds)}')
df = pd.DataFrame(columns=['Frequency (Hz)', 'Start Row', 'End Row'])
for i, pause_bound in enumerate(pause_bounds):
    pause_start, pause_end = pause_bound
    logger.info(f'|Pause {i} Start row: {max(pause_start, 0)}, End row: {pause_end}')
    if i < int(len(frequencies)):
        next_frequency = frequencies[i]
        frequency_start = pause_end - 10
        frequency_end = pause_bounds[i+1][0]+10
        frame_bounds_frequency_sorted.append([i for i in frame_bounds if i[0] >= frequency_start and i[1] <= frequency_end])
        logger.info(f'|Frequency {next_frequency} Hz between rows {frequency_start} and {frequency_end}, with {len(frame_bounds_frequency_sorted[i])} frames')
    else:
        logger.info(f'|Reached pause with no more frequencies to assign')
        break

## For Each Frequency: ##
for f_n, frame_bounds in enumerate(frame_bounds_frequency_sorted):
    frame_bounds_at_current_frequency = frame_bounds_frequency_sorted[f_n]
    frequency = frequencies[f_n]
    logger.info(f'Reading {len(frame_bounds_at_current_frequency)} frames at frequency {frequency} Hz')
    payloads = []

    # For each frame
    for i, frame_bound in enumerate(frame_bounds_at_current_frequency):
        logger.info(f'||Reading signal {i}')
        start, end = frame_bound
        logger.info(f'||Start row: {start}, End row: {end}')
        payload = determine_states(levels_and_events_csv_path, CLK, frame_bound)
        payloads.append(payload)
        logger.info(f'||Payload: {payload}')
        write_to_csv_new_row(binary_csv_path, frequency, payload)
        Hamming_distance = BER_vs_f.Hamming_distance(expected_payload, payload)
        logger.info(f'||Hamming distance: {Hamming_distance}')

    BER = BER_vs_f.calculate_BER(payloads, expected_payload, frames_per_frequency)
    logger.info(f'|Total BER for frequency {frequency} Hz: {BER}')
    write_to_csv_new_row(BER_vs_f_CSV, frequency, BER)
