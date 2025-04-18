from _SETUP_ import set_directory
set_directory()

from common.reset import reset
from m3_message_receiving.edge_detection import detect_edges_with_orig_index
from common.hamming_code import hamming_decode
from m3_message_receiving.ASK_synchronous.determine_states import determine_states
import common.binary_image as bin_img
import common.image_displaying as img_disp

# Packages
import logging
import os
import time

## Boolean flag: Choose whether to use Hamming decoding
HAMMING_DECODE = True

## Expected Image Dimensions and Chunk Parameters ##
EXPECTED_WIDTH = 128   # in pixels
EXPECTED_HEIGHT = 128  # in pixels
CHUNK_SIZE = 8         # each chunk is 8 bits (representing 8 pixels)
SIGNALS_PER_ROW = EXPECTED_WIDTH // CHUNK_SIZE  # e.g. 128/8 = 16 signals per row
expected_total_signals = EXPECTED_HEIGHT * SIGNALS_PER_ROW  # e.g. 128 * 16 = 2048

## Transmission Key Settings ##
FIRST_KEY = 3
LAST_KEY = 110  # Adjust so that TOTAL_KEYS equals the number of transmitting keys; e.g., 3 to 110 yields 108 keys.
TOTAL_KEYS = LAST_KEY - FIRST_KEY + 1  # should be 108

## Determine frame structure ##
# The transmitter sends signals round-robin over all keys.
full_frames = expected_total_signals // TOTAL_KEYS      # number of full frames
partial_frame_signals = expected_total_signals % TOTAL_KEYS # signals in the final partial frame
logging.info(f"Expected total signals: {expected_total_signals}")
logging.info(f"Full frames: {full_frames}, Partial frame signals: {partial_frame_signals}")

## Define file paths ##
log_file_path = 'files/logs/ASK_image_demodulation.log'
key_levels_and_events_folder = 'files/key_light_levels'
rgb_csv_path = 'files/spreadsheets/s5_rgb_normalised.csv'
CLK_csv_path = os.path.join(key_levels_and_events_folder, 'light_levels_CLK.csv')
SGL_csv_path = os.path.join(key_levels_and_events_folder, 'light_levels_SGL.csv')
binary_csv_path = 'files/spreadsheets/s8_binary.csv'
output_image_path = 'files/images/received_image.pbm'

# Diagnostic: Check if the log directory exists and is writable
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    print(f"Log directory '{log_dir}' does not exist. Creating it...")
    os.makedirs(log_dir, exist_ok=True)
else:
    print(f"Log directory '{log_dir}' exists.")

# Diagnostic: Check if the log file is writable
try:
    with open(log_file_path, 'w') as test_log_file:
        test_log_file.write("Log file is writable.\n")
    print(f"Log file '{log_file_path}' is writable.")
except Exception as e:
    print(f"Error: Cannot write to log file '{log_file_path}'. Exception: {e}")

# Configure the logger
logging.basicConfig(
    filename=log_file_path,
    filemode='w',  # Overwrite the log file each run
    format='%(asctime)s \t %(levelname)s \t %(message)s',
    level=logging.DEBUG  # Set to DEBUG to capture all logs
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Remove the console handler to avoid excessive terminal output
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add a file handler to ensure logs go to the file
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s \t %(levelname)s \t %(message)s'))
logger.addHandler(file_handler)

# Add a console handler for minimal terminal output (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only show errors in the terminal
console_handler.setFormatter(logging.Formatter('%(asctime)s \t %(levelname)s \t %(message)s'))
logger.addHandler(console_handler)

# Test log message
logger.info("Logger initialized successfully. Starting script...")

## Signal parameters ##
codeword_bits = 11  # for Hamming; adjust if needed
frequency = 10      # transmission frequency in Hz
camera_sample_rate = 60  # camera framerate in fps
frame_bits = codeword_bits  # for logging purposes

## Reset Files ##
reset(binary_csv_path, output_image_path, key_levels_and_events_folder)

## Read CLK and SGL Keys ##
CLK = detect_edges_with_orig_index(rgb_csv_path, 0, CLK_csv_path, threshold_fraction=0.2)
SGL = detect_edges_with_orig_index(rgb_csv_path, 3, SGL_csv_path, threshold_fraction=0.2)
frame_bounds = list(zip(SGL[::2], SGL[1::2]))  # each frame is between consecutive SGL edges
logger.info(f"Clock Flips: {len(CLK)}, Signal Flips: {len(SGL)}, Frames (per key): {len(frame_bounds)}")
logger.info(f"Bits per Frame: expected-{frame_bits}, detected-{len(CLK)/len(frame_bounds)}")

## Receive Data Chunks, grouped by transmitting key ##
# We'll store signals in a dictionary:
# Key: transmitting key, Value: list of signals (in order)
received_signals_by_key = {}

for key in range(FIRST_KEY, LAST_KEY + 1):
    received_signals_by_key[key] = []
    colour_n = key % 3
    column = (key - 1) * 3 + colour_n
    colour_dictionary = {0: 'R', 1: 'G', 2: 'B'}
    colour = colour_dictionary[colour_n]
    logger.info(f"Processing Key {key}, Colour {colour}, Column {column}")

    levels_and_events_csv_path = os.path.join(key_levels_and_events_folder, f"light_levels_key_{key}.csv")
    _ = detect_edges_with_orig_index(rgb_csv_path, column, levels_and_events_csv_path, threshold_fraction=0.1)
    logger.info(f"|Reading key {key}, column {column}")

    # For each frame bound, receive one signal (chunk) from this key.
    for frame_bound in frame_bounds:
        logger.info(f"||Processing frame for key {key}, frame_bound {frame_bound}")
        codeword = determine_states(levels_and_events_csv_path, CLK, frame_bound)
        logger.info(f"||Received codeword: {codeword}")
        if HAMMING_DECODE:
            payload = hamming_decode(codeword)
            logger.info(f"||Decoded payload (binary chunk): {payload}")
        else:
            payload = codeword
            logger.info(f"||Using raw codeword as payload: {payload}")
        received_signals_by_key[key].append(payload)

    # Determine expected signals for this key:
    # Keys with (key - FIRST_KEY) < partial_frame_signals should have (full_frames + 1) signals;
    # others should have full_frames signals.
    expected_signals = full_frames + (1 if (key - FIRST_KEY) < partial_frame_signals else 0)
    while len(received_signals_by_key[key]) < expected_signals:
        logger.warning(f"Key {key} is missing a signal for a frame; padding with zeros.")
        received_signals_by_key[key].append("0" * CHUNK_SIZE)

## Reassemble Full Signal Sequence in Round-Robin Order ##
overall_signals = []
# For each full frame, iterate through all keys.
for frame_index in range(full_frames):
    for key in range(FIRST_KEY, LAST_KEY + 1):
        overall_signals.append(received_signals_by_key[key][frame_index])
# For the final partial frame, only include signals from keys that transmitted extra.
for key in range(FIRST_KEY, FIRST_KEY + partial_frame_signals):
    overall_signals.append(received_signals_by_key[key][full_frames])

total_signals = len(overall_signals)
logger.info(f"Total signals reassembled: {total_signals}")
logger.info(f"Expected total signals: {expected_total_signals}")

## Helper function: extend_frame ##
def extend_frame(frame, expected_length):
    """Extend a frame by repeating its last bit until it reaches the expected length.
    If the frame is longer than expected, it is truncated."""
    if len(frame) < expected_length:
        frame += frame[-1] * (expected_length - len(frame))
    elif len(frame) > expected_length:
        frame = frame[:expected_length]
    return frame

## Reassemble Image Rows ##
rows = []
if total_signals < expected_total_signals:
    logger.error("Not enough signals received to reconstruct the full image!")
else:
    overall_signals = overall_signals[:expected_total_signals]  # truncate any extra signals
    for row_index in range(EXPECTED_HEIGHT):
        # Each row consists of SIGNALS_PER_ROW signals.
        row_signals = overall_signals[row_index * SIGNALS_PER_ROW:(row_index + 1) * SIGNALS_PER_ROW]
        # Extend each frame if its length is less than CHUNK_SIZE.
        extended_frames = []
        for i, frame in enumerate(row_signals):
            if len(frame) < CHUNK_SIZE:
                erroneous_frame = frame
                frame = extend_frame(erroneous_frame, CHUNK_SIZE)
                logger.info(f"Extending frame {i}: {erroneous_frame}   ->   {frame}")
            extended_frames.append(frame)
        row_bin_str = "".join(extended_frames)
        logger.info(f"Row {row_index+1}: {row_bin_str}")
        # Convert the binary string into a list of integers (pixels)
        row = [int(bit) for bit in row_bin_str]
        rows.append(row)

## Write the Received Image ##
bin_img.write_p1_from_rows(rows, output_image_path)
logger.info(f"Received image saved to {output_image_path}")
bin_img.display_pgm_or_pbm(output_image_path)
bin_img.compare_pbm_files('files/images/dog_P1.pbm', output_image_path, 'files/images/received_image_diff.png')
img_disp.display_image('files/images/received_image_diff.png')