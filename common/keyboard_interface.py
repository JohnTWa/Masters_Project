from cuesdk import CueSdk
import time

def keyboard_setup():
    sdk = CueSdk()
    
    def on_state_changed(evt):
        print("Session state:", evt.state)
        
    err = sdk.connect(on_state_changed)
    details, err = sdk.get_session_details()
    print("Session details:", details)
    device_id = '{d9905297-d6d8-48b7-ac33-94e8ca286e24}' # K70 keyboard
    
    class CorsairLedColor:
        def __init__(self, id, r, g, b, a=255):
            self.id = id
            self.r = r
            self.g = g
            self.b = b
            self.a = a
    return sdk, device_id, CorsairLedColor

def set_colour(setup_items: list, key_IDs: list, colour: tuple):
    '''
    Set key_IDs to single (r,g,b) colour.

    '''
    colours = [colour]*len(key_IDs)
    result = set_colours(setup_items, key_IDs, colours)
    return result

def set_colours(setup_items: list, key_IDs: list, colours: list):
    '''
    Set key_IDs to list of (r,g,b) colours.

    '''
    sdk, device_id, CorsairLedColor = setup_items
    led_colours = []
    for i, ID in enumerate(key_IDs):
        r, g, b = colours[i]
        if ID == 0: # Deal with Corsair logo
            led_colours.append(CorsairLedColor(id=196609, r=r, g=g, b=b))
            led_colours.append(CorsairLedColor(id=196610, r=r, g=g, b=b))
        else:
            led_colours.append(CorsairLedColor(id=ID, r=r, g=g, b=b))
    result = sdk.set_led_colors(device_id, led_colours)
    return result

def set_colour_timed(setup_items: list, key_IDs: list, colour: tuple, time_length: float, verbose: int = 0):
    '''
    Set key_IDs to uniform colour for time_length seconds.

    '''

    # Start counting and split lists
    start_time = time.perf_counter()
    result = set_colour(setup_items, key_IDs, colour)

    if verbose: 
        if result != 0:
            print(f'Error setting keys to uniform colour {colour}: {result}')
        else:
            print(f"Setting keys set to {colour} for {time_length} seconds.")
    
    # Ensure perfect timing
    elapsed = time.perf_counter() - start_time
    remaining = time_length - elapsed
    if remaining > 0:
        time.sleep(remaining)

def set_colours_timed(setup_items: list, key_IDs: list, colours: list, time_length: float, verbose: int = 0):
    '''
    Set key_IDs to colour for time_length seconds.

    '''

    # Start counting and split lists
    start_time = time.perf_counter()
    result = set_colours(setup_items, key_IDs, colours)

    if verbose: 
        if result != 0:
            print(f'Error setting keys to colours: {result}')
        else:
            print(f"Setting keys set to colours for {time_length} seconds.")

    # Ensure perfect timing
    elapsed = time.perf_counter() - start_time
    remaining = time_length - elapsed
    if remaining > 0:
        time.sleep(remaining)