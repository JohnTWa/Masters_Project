from _SETUP_ import set_directory
set_directory()

import time
from common.file_handling import csv_to_tuple
from common.ASCII import file_to_ascii_binary
from m1_transmitting.modulation.formatting import FSK_format, MFSK_format
from m1_transmitting.modulation.FSK_modulation import keyboard_setup, transmit_sine_wave, transmit_triangle_wave

def FSK_main():
    ## Define transmission parameters ##

    frequency_set = (1, 2)
    T_bit = 2

    ## Define file paths ##

    key_ids_path = 'files/spreadsheets/s1_key_IDs.csv'
    transmission_text_path = 'files/t1_transmission_text.txt'

    ## Determine key IDs ##

    key_IDs = csv_to_tuple(key_ids_path)

    ## Encode and Format the data ##

    binary_data = file_to_ascii_binary(transmission_text_path) 
    frequency_frames = []
    for binary_frame in binary_data:
        frequency_frames.append(MFSK_format(binary_frame, frequency_set))
    print(f'Frequency frames: {frequency_frames}')

    sdk, device_id, CorsairLedColor = keyboard_setup()
    time.sleep(1)

    ## Transmit the signals ##

    for frequency_frame in frequency_frames:
        print(f'Frequencies for frame: {frequency_frame}')
        for f in frequency_frame:
            print(f'Frequency: {f},')
            print(f'Periods: {int(T_bit*f)}')
            transmit_sine_wave(
                sdk=sdk,
                device_id=device_id,
                CorsairLedColor=CorsairLedColor,
                data_keys=key_IDs,
                frequency=f,
                periods=int(T_bit*f),
                colour=(255, 0, 0),
                SAMPLES_PER_PERIOD=60
            )