from _SETUP_ import set_directory
set_directory()

from common.file_handling import csv_to_list, adjust_for_Corsair_logo
import common.keyboard_interface as keyboard
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
        keyboard.set_colours_timed(setup_items, key_IDs, colours, bit_period)

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
        keyboard.set_colours_timed(setup_items, keys_to_use, colours, bit_period)

def send_binary_signals_with_CLK_and_SGL(setup_items, binary_signals, data_ids, CLK_ids, SGL_ids, frequency):
    """
    Sends binary signals on transmission keys of a Corsair keyboard, using one binary signal per data key
    (with alternating RGB "ON" colors per key), while also sending a CLK signal (toggled once per bit)
    and an SGL signal (high during transmission). After the data/SGL lines are turned off,
    CLK lines are turned off after an additional half-bit period.
    
    This version uses keyboard.set_colours_timed to update colors.
    
    Parameters:
      - setup_items (list): The items returned by keyboard_setup() [sdk, device_id, CorsairLedColor].
      - binary_signals (list): List of binary signal strings (e.g. ['101100011', '101101100', ...]).
      - data_ids (list): Key IDs for the data signals.
      - CLK_ids (list): Key IDs for the clock signal(s).
      - SGL_ids (list): Key IDs for the SGL signal(s).
      - frequency (float): Frequency in Hz (data changes every 1/frequency).
    """

    # ─────────────────────────────────────────────────────────────
    # 1) Basic validation and key overlap checking
    # ─────────────────────────────────────────────────────────────
    if not binary_signals:
        print("No signals provided.")
        return

    signal_length = len(binary_signals[0])
    if not all(len(sig) == signal_length for sig in binary_signals):
        print("Error: All binary signals must be of equal length.")
        return

    data_set, clk_set, sgl_set = set(data_ids), set(CLK_ids), set(SGL_ids)
    if data_set.intersection(clk_set) or data_set.intersection(sgl_set) or clk_set.intersection(sgl_set):
        raise ValueError("Key overlap found among data, CLK, or SGL keys.")

    if len(binary_signals) > len(data_ids):
        print(f"Warning: More binary signals ({len(binary_signals)}) than data keys ({len(data_ids)}). "
              f"Only the first {len(data_ids)} signals will be used.")
        binary_signals = binary_signals[:len(data_ids)]
    elif len(binary_signals) < len(data_ids):
        print(f"Warning: More data keys ({len(data_ids)}) than binary signals ({len(binary_signals)}). "
              "Extra keys will be off.")
        binary_signals += ['0' * signal_length] * (len(data_ids) - len(binary_signals))

    # ─────────────────────────────────────────────────────────────
    # 2) Set up SDK and timing variables
    # ─────────────────────────────────────────────────────────────
    sdk, device_id, CorsairLedColor = setup_items
    period = 1.0 / frequency
    half_period = period / 2.0

    # Define the ON colors for each channel (cycling red, green, blue for data keys)
    channels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    clock_state = 0  # start with CLK off

    # Pre-calculate SGL "on" color (white)
    sgl_on_color = (255, 0, 0)

    # Build the complete key list for combined updates:
    all_keys = data_ids + CLK_ids + SGL_ids

    # ─────────────────────────────────────────────────────────────
    # 3) Turn SGL on (start of transmission)
    # ─────────────────────────────────────────────────────────────
    # Use set_colours_timed for SGL keys only (uniform white, with zero delay)
    keyboard.set_colour_timed(setup_items, SGL_ids, sgl_on_color, 0)

    # ─────────────────────────────────────────────────────────────
    # 4) Transmit signals bit by bit
    # ─────────────────────────────────────────────────────────────
    for bit_index in range(signal_length):
        start_time = time.perf_counter()

        # Build data colors: one binary signal per key, using alternating channel colors.
        data_colours = []
        for i, sig in enumerate(binary_signals):
            if sig[bit_index] == '1':
                data_colours.append(channels[i % len(channels)])
            else:
                data_colours.append((0, 0, 0))

        # Helper to build CLK colors for current state:
        def build_clk_colours(state):
            if state == 1:
                return [(255, 0, 0)] * len(CLK_ids)
            else:
                return [(0, 0, 0)] * len(CLK_ids)

        # First half: use current clock_state
        clk_colours_first = build_clk_colours(clock_state)
        # For SGL keys, always use the on color.
        sgl_colours = [sgl_on_color] * len(SGL_ids)
        # Concatenate colors in same order as all_keys: data_ids, CLK_ids, then SGL_ids.
        colours_first = data_colours + clk_colours_first + sgl_colours
        keyboard.set_colours_timed(setup_items, all_keys, colours_first, half_period)
        
        # Toggle clock state for the second half
        clock_state = 1 - clock_state
        clk_colours_second = build_clk_colours(clock_state)
        colours_second = data_colours + clk_colours_second + sgl_colours
        keyboard.set_colours_timed(setup_items, all_keys, colours_second, half_period)

        bit_duration = time.perf_counter() - start_time
        print(f"Bit #{bit_index + 1} displayed for {bit_duration:.6f} seconds")

    # ─────────────────────────────────────────────────────────────
    # 5) Turn off data & SGL, then finally CLK (with extra half-bit delay)
    # ─────────────────────────────────────────────────────────────
    off_color = (0, 0, 0)
    # Turn off data and SGL keys first:
    data_sgl_keys = data_ids + SGL_ids
    off_data_sgl = [off_color] * len(data_sgl_keys)
    keyboard.set_colours_timed(setup_items, data_sgl_keys, off_data_sgl, half_period)
    
    # Then, after an extra half-period, turn off CLK keys:
    keyboard.set_colours_timed(setup_items, CLK_ids, [off_color] * len(CLK_ids), half_period)

if __name__ == "__main__":

    key_IDs = csv_to_list("files/spreadsheets/s1_key_IDs.csv")
    print(key_IDs)   

    key_IDs = adjust_for_Corsair_logo(key_IDs)
    print(key_IDs)
    sdk, device_id, CorsairLedColor = keyboard.keyboard_setup()
    setup_items = [sdk, device_id, CorsairLedColor]

    CLK_IDs = [0]
    SGL_IDs = [1]
    data_IDs = key_IDs.copy()
    data_IDs.remove(CLK_IDs[0])
    data_IDs.remove(SGL_IDs[0])

    time.sleep(0.1)
    
    keyboard.set_colour_timed(setup_items, key_IDs, (255, 0, 0), 5)
    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), 1)
    send_binary_signals_with_CLK_and_SGL(setup_items,
                                        binary_signals=['10110001']*len(key_IDs),
                                        data_ids=data_IDs,
                                        CLK_ids=[0],
                                        SGL_ids=[1],
                                        frequency=10)
    keyboard.set_colour_timed(setup_items, key_IDs, (0, 0, 0), 1)