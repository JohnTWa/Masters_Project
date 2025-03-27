from _SETUP_ import set_directory
set_directory()

import time
import os

# Local Functions
import common.file_handling as fh
import m1_transmitting.modulation.formatting as fmt
from common.hamming_code import hamming_encode
import common.ASCII as ASCII
import common.keyboard_interface as keyboard
import m1_transmitting.modulation.ASK_modulation as modulation
import common.binary_image as bin_img

## Define file paths ##
key_ids_path = 'files/key_IDs.csv'
data_ids_path = 'files/data_IDs.csv'
image_path = 'files\images\dog.jpg'
p4_image_path = f'{os.path.splitext(image_path)[0]}_P4.pbm'
p1_image_path = f'{os.path.splitext(image_path)[0]}_P1.pbm'

## Define transmission parameters ##
pause_time = 1
frequency = 10
framerate = 60
idle_bits = 1
HAMMING_ENCODE = False

## Load keys ##
key_IDs = fh.csv_to_list("files/spreadsheets/s1_key_IDs.csv")
key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
CLK_IDs = [0]
SGL_IDs = [1]
data_IDs = key_IDs.copy()
data_IDs.remove(CLK_IDs[0])
data_IDs.remove(SGL_IDs[0])
n_data_keys = len(data_IDs)

## Process Image ##

bin_img.display_pgm_or_pbm(image_path)
bin_img.image_to_pbm(image_path, p4_image_path, 256)
bin_img.convert_p4_to_p1(p4_image_path, p1_image_path)
bin_img.display_pgm_or_pbm(p1_image_path)

# Split the ASCII PBM into chunks of 8 bits
rows = bin_img.split_pbm_rows(p1_image_path)
rows_of_chunks = []
for row in rows:
    chunks = (bin_img.split_row_into_8bit_chunks(row))
    rows_of_chunks.append(chunks)

## Create Signals ##
# For each 8-bit chunk, convert the bits to a string and then encode using hamming code.
signals = []
for row_chunks in rows_of_chunks:
    for chunk in row_chunks:
        # Convert chunk (list of ints) to a string like "10101010"
        chunk_str = "".join(str(bit) for bit in chunk)

        if HAMMING_ENCODE:
            codeword = hamming_encode(chunk_str)
            signals.append(codeword)
        else: 
            signals.append(chunk_str)

# Split the list of signals into sets that can be transmitted using your available keys.
signal_sets = ASCII.list_splitting(signals, round(n_data_keys))

## Transmit the Signals ##
setup_items = keyboard.keyboard_setup()
time.sleep(0.1)

keyboard.set_colour_timed(setup_items, key_IDs, (255, 0, 0), 4)

for signal_set in signal_sets:
    modulation.send_binary_signals_with_CLK_and_SGL(
        setup_items,
        binary_signals=signal_set,
        data_ids=data_IDs,
        CLK_ids=CLK_IDs,
        SGL_ids=SGL_IDs,
        frequency=frequency
    )

keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), 4)