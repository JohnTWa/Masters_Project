from _SETUP_ import set_directory
set_directory()

import time
import common.file_handling as fh
from common.ASCII import file_to_ascii_binary
from m1_transmitting.modulation.formatting import FSK_format, MFSK_format
import m1_transmitting.modulation.FSK_modulation as mod
import common.keyboard_interface as keyboard

def FSK_main(binary_frame='10110001'):
    ## Define transmission parameters ##
    frequency_set = (1, 2)
    T_bit = 2

    ## Define file paths ##
    key_ids_path = 'files/spreadsheets/s1_key_IDs.csv'
    transmission_text_path = 'files/t1_transmission_text.txt'

    ## Determine key IDs ##
    key_IDs = fh.csv_to_list(key_ids_path)
    key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
    sdk, device_id, CorsairLedColor = keyboard.keyboard_setup()
    setup_items = [sdk, device_id, CorsairLedColor]

    ## Encode and Format the data ##
    frequency_frame = MFSK_format(binary_frame, frequency_set)
    print(f'Frequency frame: {frequency_frame}')

    setup_items = keyboard.keyboard_setup()
    time.sleep(1)

    ## Transmit the signals ##
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 0, 0), 4)
    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), 1)
    for f in frequency_frame:
        print(f'Frequency: {f},')
        print(f'Periods: {int(T_bit*f)}')
        mod.single_sine_wave(
            setup_items,
            key_IDs,
            frequency=f,
            T_symbol=2,
            colour=(255, 0, 0),
        )
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 255, 255), 1)

if __name__ == '__main__':
    FSK_main()