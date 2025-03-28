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

def process_image(image_path):
    p4_image_path = f'{os.path.splitext(image_path)[0]}_P4.pbm'
    p1_image_path = f'{os.path.splitext(image_path)[0]}_P1.pbm'
    bin_img.display_pgm_or_pbm(image_path)
    bin_img.image_to_pbm(image_path, p4_image_path, 128)
    bin_img.convert_p4_to_p1(p4_image_path, p1_image_path)
    bin_img.display_pgm_or_pbm(p1_image_path)

    return p1_image_path

def transmit_image_using_ASK(key_IDs, p1_image_path, frequency, HAMMING_ENCODE=False):
    key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
    CLK_IDs = [0] #Corsair Logo
    SGL_IDs = [1] #ESC
    data_IDs = key_IDs.copy()
    data_IDs.remove(CLK_IDs[0])
    data_IDs.remove(SGL_IDs[0])
    n_data_keys = len(data_IDs)

    # Split the ASCII PBM into chunks of 8 bits
    rows = bin_img.split_pbm_rows(p1_image_path)
    rows_of_chunks = []
    for row in rows:
        chunks = bin_img.split_row_into_8bit_chunks(row)
        rows_of_chunks.append(chunks)

    ## Create Signals ##
    # For each 8-bit chunk, convert the bits to a string and then encode using Hamming code (if enabled).
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

    # Calculate and print the expected transmission time.
    # Each signal (e.g., "10101010") has a length of 8 bits (or 11 bits if Hamming encoding is used).
    signal_length = len(signal_sets[0][0]) + 1  # use the first signal in the first set.
    number_of_sets = len(signal_sets)
    t1 = 4
    t2 = 1
    expected_time = number_of_sets * (signal_length / frequency) + t1 + t2

    print(f"Expected transmission time: {expected_time:.2f} seconds")

    start_time = time.perf_counter() #START
    setup_items = keyboard.keyboard_setup()
    time.sleep(0.1)
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 0, 0), t1)
    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), t2)

    for signal_set in signal_sets:
        modulation.send_binary_signals_with_CLK_and_SGL(
            setup_items,
            binary_signals=signal_set,
            data_ids=data_IDs,
            CLK_ids=CLK_IDs,
            SGL_ids=SGL_IDs,
            frequency=frequency
        )
    end_time = time.perf_counter()  # end timing the transmission

    actual_time = end_time - start_time
    print(f"Actual transmission time: {actual_time:.2f} seconds")

    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), t2) 

if __name__ == '__main__':
    ## Define file paths ##
    key_ids_path = 'files/spreadsheets/s1_key_IDs.csv'
    image_path = 'files/images/dog.png'

    ## Define transmission parameters ##
    pause_time = 1
    frequency = 10
    framerate = 60
    idle_bits = 1
    HAMMING_ENCODE = False

    ## Process image ##
    p1_image_path = process_image(image_path)

    ## Load keys ##
    key_IDs = fh.csv_to_list(key_ids_path)

    #### MAIN FUNCTION ####
    for frequency in [10, 15]:
        transmit_image_using_ASK(key_IDs, p1_image_path, frequency, HAMMING_ENCODE)