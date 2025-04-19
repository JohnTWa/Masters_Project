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
frequencies = list(range(10, 31))  # Frequencies from 1 to 30 Hz
framerate = 60
idle_bits = 1
payload = '10110001'
frames_per_frequency = 20

## Load keys ##
key_IDs = fh.csv_to_list("files/spreadsheets/s1_key_IDs.csv")
key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
CLK_IDs = [0]
SGL_IDs = [1]
data_IDs = key_IDs.copy()
data_IDs.remove(CLK_IDs[0])
data_IDs.remove(SGL_IDs[0])
n_data_keys = len(data_IDs)
print(data_IDs)

## Calculate Transmission Time ##
bit_periods_per_frame = len(payload) + 2.5
transmission_time = 0
for frequency in frequencies:
    transmission_time += frames_per_frequency*bit_periods_per_frame/frequency
print(f"Transmission time: {transmission_time/60:.2f} mins")

## Transmit the signals ##

setup_items = keyboard.keyboard_setup()
time.sleep(0.1)

keyboard.set_colour_timed(setup_items, key_IDs, (255,0,0), 4)
keyboard.set_colour_timed(setup_items, key_IDs, (0,0,0), 1)

for frequency in frequencies:

    print(f"Frequency: {frequency} Hz")
    i = 0
    while i < 20:
        modulation.send_binary_signals_with_CLK_and_SGL(setup_items,
                                            binary_signals=[payload]*n_data_keys,
                                            data_ids=data_IDs,
                                            CLK_ids=CLK_IDs,
                                            SGL_ids=SGL_IDs,
                                            frequency=frequency)
        i += 1
    time.sleep(pause_time)
    
keyboard.set_colour_timed(setup_items, key_IDs, (0,0,0), 1)