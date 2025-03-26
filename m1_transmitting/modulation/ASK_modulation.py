from _SETUP_ import set_directory
set_directory()

from common.file_handling import csv_to_list, adjust_for_Corsair_logo
from common.keyboard_interface import keyboard_setup, set_colour_timed, set_colours_timed
import time

def send_binary_signals_alternating_RGB(setup_items, binary_signals, key_IDs, frequency):
    """
    Sends binary signals so that each key transmits one signal, and each neighbouring key is a different colour.
    """
    bit_period = 1 / frequency
    n_bits = len(binary_signals[0])
    n_signals = len(binary_signals)
    
    # Define the ON colors for each channel in cyclic order.
    channels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    # For each bit position in the signal
    for bit_position in range(n_bits):
        colours = []
        # Iterate over each signal (each signal will map to a key)
        for i in range(n_signals):
            # Only process if a corresponding key exists
            if i < len(key_IDs):
                # If the bit is '1', use the channel color assigned to this key's order;
                # otherwise, use (0, 0, 0).
                if binary_signals[i][bit_position] == '1':
                    colour = channels[i % 3]
                else:
                    colour = (0, 0, 0)
                colours.append(colour)
        # If there are more keys than signals, fill the rest with black.
        extra_keys = len(key_IDs) - len(colours)
        if extra_keys > 0:
            colours.extend([(0, 0, 0)] * extra_keys)
        
        # Update the keyboard colors for the current bit position
        set_colours_timed(setup_items, key_IDs, colours, bit_period)


def send_binary_signals(setup_items, binary_signals, key_IDs, frequency):
    '''
    Sends binary signals with one signal for each colour in each key (3 signals per key)
    assigned according to order.
    '''
    bit_period = 1 / frequency
    n_bits = len(binary_signals[0])
    n_signals = len(binary_signals)

    # Split binary_signals into chunks of 3 (each chunk corresponds to one key)
    grouped_signals = []
    for i in range(0, n_signals, 3):
        grouped_signals.append(binary_signals[i:i+3])

    # For each bit position
    for bit_position in range(n_bits):
        colours = []
        # For each group (each key with signals)
        for three_signals in grouped_signals:
            colour = []
            for signal in three_signals:
                if signal[bit_position] == '1':
                    colour.append(255)
                else:
                    colour.append(0)
            # Convert the list into a tuple (R, G, B)
            colours.append((colour[0], colour[1], colour[2]))
        
        # If there are more keys than groups, fill extra keys with (0,0,0)
        n_signal_keys = len(colours)
        total_keys = len(key_IDs)
        if total_keys > n_signal_keys:
            extra_keys_count = total_keys - n_signal_keys
            colours.extend([(0, 0, 0)] * extra_keys_count)
            keys_to_use = key_IDs  # use all provided keys
        else:
            keys_to_use = key_IDs[:n_signal_keys]

        # Set colours for all keys at the current bit position
        set_colours_timed(setup_items, keys_to_use, colours, bit_period)

if __name__ == "__main__":

    key_IDs = csv_to_list("files/spreadsheets/s1_key_IDs.csv")
    print(key_IDs)   

    key_IDs = adjust_for_Corsair_logo(key_IDs)
    print(key_IDs)
    sdk, device_id, CorsairLedColor = keyboard_setup()
    setup_items = [sdk, device_id, CorsairLedColor]

    time.sleep(0.1)
    set_colour_timed(setup_items, key_IDs, (255, 0, 0), 5)
    set_colour_timed(setup_items, key_IDs, (0, 0, 0), 0.5)
    send_binary_signals_alternating_RGB(setup_items, 
                                        binary_signals=['1101100011']*len(key_IDs), 
                                        key_IDs=key_IDs, 
                                        frequency=10)  