from _SETUP_ import set_directory
set_directory()

# Packages
import time

# Local Functions
import common.file_handling as fh
import m1_transmitting.modulation.formatting as fmt
from common.hamming_code import hamming_encode
import common.ASCII as ASCII
import common.keyboard_interface as keyboard
import m1_transmitting.modulation.ASK_modulation as modulation

## Define transmission parameters ##

key_ids_path = 'files/key_IDs.csv'
data_ids_path = 'files/data_IDs.csv'
transmission_text_path = 'files/t1_transmission_text.txt'
pause_time = 1
frequency = 10
framerate = 60
idle_bits = 1

## Load keys ##
key_IDs = fh.csv_to_list("files/spreadsheets/s1_key_IDs.csv")
key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
CLK_IDs = [0]
SGL_IDs = [1]
data_IDs = key_IDs.copy()
data_IDs.remove(CLK_IDs[0])
data_IDs.remove(SGL_IDs[0])
n_data_keys = len(data_IDs)

## Process Text ##
binary_data = ASCII.file_to_ascii_binary(transmission_text_path)  

signals = []
for data in binary_data:

    codeword = hamming_encode(data)
    signals.append(codeword)

signal_bits = len(signals[0])
signal_sets = ASCII.list_splitting(signals, round(n_data_keys))

## Transmit the signals ##

setup_items = keyboard.keyboard_setup()
time.sleep(0.1)

keyboard.set_colour_timed(setup_items, key_IDs, (255,0,0), 4)

for signal_set in signal_sets:

    modulation.send_binary_signals_with_CLK_and_SGL(setup_items,
                                        binary_signals=signal_set,
                                        data_ids=data_IDs,
                                        CLK_ids=CLK_IDs,
                                        SGL_ids=SGL_IDs,
                                        frequency=10)
    
keyboard.set_colour_timed(setup_items, key_IDs, (0,0,0), 4)