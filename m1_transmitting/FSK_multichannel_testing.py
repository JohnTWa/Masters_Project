from _SETUP_ import set_directory
set_directory()

import time
import common.file_handling as fh
from common.ASCII import file_to_ascii_binary
from m1_transmitting.modulation.formatting import FSK_format, MFSK_format
import m1_transmitting.modulation.FSK_modulation as mod
import common.keyboard_interface as keyboard

def FSK_main(binary_frames=('10110001', '11001010', '00111001')):
    ## Define transmission parameters ##
    frequency_set = (0.5, 1, 1.5, 2)
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
    frequency_frames = []
    for i, binary_frame in enumerate(binary_frames):
        frequency_frame = MFSK_format(binary_frame, frequency_set)
        print(f'Frame {i+1}: {frequency_frame}')
        frequency_frames.append(frequency_frame)

    setup_items = keyboard.keyboard_setup()
    time.sleep(1)

    ## Transmit the signals ##
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 0, 0), 4)
    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), 1)
    keyboard.set_colour_timed(setup_items, key_IDs, (127, 127, 127), 1)
    
    for symbol_position in range(len(frequency_frames[0])):
        
        R_frequency = frequency_frames[0][symbol_position]
        G_frequency = frequency_frames[1][symbol_position]
        B_frequency = frequency_frames[2][symbol_position]

        bits_per_symbol = len(binary_frames[0])/len(frequency_frames[0])
        print(f'Bits Per Symbol: {bits_per_symbol}')
        bit_position = int((symbol_position+1)*bits_per_symbol)
        R_bits = binary_frames[0][0:bit_position]
        R_bits = binary_frames[1][0:bit_position]
        R_bits = binary_frames[2][0:bit_position]

        print(f'R: {binary_frames[0][symbol_position]}, G: {binary_frames[1][symbol_position]}, B: {binary_frames[2][symbol_position]}')
        print(f'R frequency: {R_frequency}, G frequency: {G_frequency}, B frequency: {B_frequency}')
        mod.multichannel_sine_waves(
            setup_items, 
            key_IDs, 
            R_frequency, 
            G_frequency, 
            B_frequency,
            T_symbol=2
        )
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 255, 255), 1)

if __name__ == '__main__':
    FSK_main()