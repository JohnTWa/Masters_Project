from _SETUP_ import set_directory
set_directory()

import time
from common.file_handling import csv_to_list, adjust_for_Corsair_logo
from common.keyboard_interface import keyboard_setup, set_colours_timed, set_colour_timed

def set_alternating_colours(setup_items: list, 
                            key_IDs: list, 
                            time_length: float, 
                            alternating_colour_set=[(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)],
                            verbose: int = 0,
                            ):
    '''
    Set key_IDs to R, G, B and OFF according to order for time_length seconds.

    '''

    # Set colours
    colours = []
    for i, ID in enumerate(key_IDs):
        _, remainder = divmod(i, len(alternating_colour_set))
        colours.append(alternating_colour_set[remainder])

    result = set_colours_timed(setup_items, key_IDs, colours, time_length)

if __name__ == "__main__":

    key_IDs = csv_to_list("files/spreadsheets/s1_key_IDs.csv")
    print(key_IDs)   

    key_IDs = adjust_for_Corsair_logo(key_IDs)
    print(key_IDs)
    sdk, device_id, CorsairLedColor = keyboard_setup()

    time.sleep(1)
    setup_items = [sdk, device_id, CorsairLedColor]

    set_colour_timed(setup_items, key_IDs, colour=(255, 0, 0), time_length=2, verbose=1)
    set_colour_timed(setup_items, key_IDs, colour=(0, 0, 0), time_length=1, verbose=1)
    set_colour_timed(setup_items, key_IDs, colour=(255, 255, 255), time_length=1, verbose=1)
    set_alternating_colours(setup_items, key_IDs, time_length=10)