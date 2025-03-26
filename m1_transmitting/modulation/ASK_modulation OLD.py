from cuesdk import CueSdk
import time

def keyboard_setup():

    sdk = CueSdk()
    def on_state_changed(evt):
        print(evt.state)
    err = sdk.connect(on_state_changed)
    details, err = sdk.get_session_details()
    print(details)
    device_id = '{d9905297-d6d8-48b7-ac33-94e8ca286e24}'

        # Define a class for LED colors
    class CorsairLedColor:
        def __init__(self, id, r, g, b, a=255):
            self.id = id
            self.r = r
            self.g = g
            self.b = b
            self.a = a
    
    return sdk, device_id, CorsairLedColor

def send_binary_signal(binary_signal, key_ids, frequency):
    """
    Sends a binary signal as a string to specified keys on a Corsair device using the provided frequency.
    
    Parameters:
    - binary_signal (str): The binary signal to transmit, represented as a string (e.g., "101010").
    - key_ids (list or tuple): List or tuple of key IDs to control.
    - frequency (float): The frequency (Hz) at which bits are transmitted.
    """
    import time

    # Ensure the input is a string of '0' and '1'
    if not isinstance(binary_signal, str) or not all(bit in '01' for bit in binary_signal):
        raise ValueError("binary_signal must be a string containing only '0' and '1'.")
    if not isinstance(key_ids, (list, tuple)):
        raise ValueError("key_ids must be a list or tuple.")

    sdk, device_id, CorsairLedColor = keyboard_setup()
    # positions = sdk.get_led_positions(device_id)
    # print(positions)

    # Define colors
    colour_1 = (255, 0, 0)   # Red for '1'
    colour_2 = (0, 0, 0)    # Off for '0'

    # Calculate the target period between bit transmissions
    period = 1 / frequency  # Frequency in Hz -> period in seconds

    # Transmit each bit in the binary signal
    for index, bit in enumerate(binary_signal):
        # Set the color for all keys based on the bit value
        color = colour_1 if bit == '1' else colour_2
        led_colors = [CorsairLedColor(id=key_id, r=color[0], g=color[1], b=color[2]) for key_id in key_ids]

        # Measure start time for each bit
        bit_start_time = time.perf_counter()

        # Set colors for all keys simultaneously
        result = sdk.set_led_colors(device_id, led_colors)
        if result != 0:  # Check if the LED color was set successfully
            print(f"Failed to set colors for keys {key_ids} bit {bit}: {result}")

        # Adjust the delay to account for the latency
        latency = time.perf_counter() - bit_start_time
        adjusted_delay = max(0, period - latency)  # Ensure non-negative delay
        time.sleep(adjusted_delay)

        # Measure end time for each bit and calculate the duration
        bit_end_time = time.perf_counter()
        bit_duration = bit_end_time - bit_start_time
        print(f"Bit #{index + 1} ({bit}) displayed for {bit_duration:.6f} seconds")

    # Turn off all keys at the end of the transmission
    led_colors_off = [CorsairLedColor(id=key_id, r=0, g=0, b=0) for key_id in key_ids]
    sdk.set_led_colors(device_id, led_colors_off)

def send_binary_signals(binary_signals, key_ids, frequency):
    """
    Sends binary signals on specific keys and colors of a Corsair keyboard, assigning signals in groups
    of three to RGB channels (red, green, blue) for each key.

    Parameters:
    - binary_signals (list or tuple): Binary signal strings to send (e.g., ['101100011', '101101100']).
    - key_ids (list or tuple): Key IDs to which signals are assigned (e.g., [1, 5, 8]).
    - frequency (float): Frequency in Hz for flashing the signals.
    """
    import time

    # Ensure all signals are of equal length
    signal_length = len(binary_signals[0])
    if not all(len(signal) == signal_length for signal in binary_signals):
        print("Error: All binary signals must be of equal length.")
        return

    # Ensure no duplicate key IDs
    if len(set(key_ids)) != len(key_ids):
        print("Error: Duplicate key IDs are not allowed.")
        return

    # Warn if there are more keys than signals
    if len(binary_signals) < len(key_ids):
        print(f"Warning: Fewer signals ({len(binary_signals)}) than keys ({len(key_ids)}). "
              f"Only the first {len(binary_signals)} keys will be used.")

    # Assign signals to keys in groups of three
    signals_per_key = 3
    key_signal_mapping = {}
    for i, signal in enumerate(binary_signals):
        key_index = i // signals_per_key
        if key_index >= len(key_ids):
            break
        key = key_ids[key_index]
        if key not in key_signal_mapping:
            key_signal_mapping[key] = []
        key_signal_mapping[key].append(signal)

    # Initialize Corsair SDK
    sdk, device_id, CorsairLedColor = keyboard_setup()

    # Define RGB values for colors
    color_rgb = {'r': (255, 0, 0), 'g': (0, 255, 0), 'b': (0, 0, 255)}

    # Transmit signals
    period = 1 / frequency
    color_order = ['r', 'g', 'b']
    for bit_index in range(signal_length):
        bit_start_time = time.perf_counter()
        led_colors = []

        for key_id, signals in key_signal_mapping.items():
            r, g, b = 0, 0, 0
            for signal_index, signal in enumerate(signals):
                color = color_order[signal_index % 3]
                bit = signal[bit_index]
                if bit == '1':
                    r_c, g_c, b_c = color_rgb[color]
                    r += r_c
                    g += g_c
                    b += b_c
            # Ensure RGB values do not exceed 255
            r = min(r, 255)
            g = min(g, 255)
            b = min(b, 255)

            led_color = CorsairLedColor(id=key_id, r=r, g=g, b=b)
            led_colors.append(led_color)

        # Set the colors for all keys simultaneously
        result = sdk.set_led_colors(device_id, led_colors)
        if result != 0:
            print(f"Failed to set colors for keys at bit {bit_index + 1}: {result}")

        # Adjust the delay to account for the latency
        latency = time.perf_counter() - bit_start_time
        time.sleep(max(0, period - latency))

    # Turn off all keys at the end of the transmission
    led_colors_off = [CorsairLedColor(id=key_id, r=0, g=0, b=0) for key_id in key_signal_mapping]
    sdk.set_led_colors(device_id, led_colors_off)

def send_binary_signals_red(binary_signals, key_ids, frequency):
    """
    Sends binary signals on specific keys using red color on a Corsair keyboard.

    Parameters:
    - binary_signals (list or tuple): Binary signal strings to send (e.g., ['101100011', '101101100']).
    - key_ids (list or tuple): Key IDs to which signals are assigned (e.g., [1, 4, 5, 9, 3]).
    - frequency (float): Frequency in Hz for flashing the signals.
    """
    import time

    # Ensure all signals are of equal length
    signal_length = len(binary_signals[0])
    if not all(len(signal) == signal_length for signal in binary_signals):
        print("Error: All binary signals must be of equal length.")
        return

    # Ensure no duplicate key IDs
    if len(set(key_ids)) != len(key_ids):
        print("Error: Duplicate key IDs are not allowed.")
        return

    # Warn if there are more keys than signals
    if len(binary_signals) < len(key_ids):
        print(f"Warning: Fewer signals ({len(binary_signals)}) than keys ({len(key_ids)}). "
              f"Only the first {len(binary_signals)} keys will be used.")
        key_ids = key_ids[:len(binary_signals)]

    # Map signals to keys
    key_signal_mapping = dict(zip(key_ids, binary_signals))

    # Initialize Corsair SDK
    sdk, device_id, CorsairLedColor = keyboard_setup()

    # Define red color RGB values
    red_rgb = (255, 0, 0)

    # Transmit signals
    period = 1 / frequency
    for bit_index in range(signal_length):
        bit_start_time = time.perf_counter()
        led_colors = []

        for key_id, signal in key_signal_mapping.items():
            bit = signal[bit_index]
            r, g, b = (red_rgb if bit == '1' else (0, 0, 0))
            led_color = CorsairLedColor(id=key_id, r=r, g=g, b=b)
            led_colors.append(led_color)

        # Set the colors for all keys simultaneously
        result = sdk.set_led_colors(device_id, led_colors)
        if result != 0:
            print(f"Failed to set colors for keys at bit {bit_index + 1}: {result}")

        # Adjust the delay to account for the latency
        latency = time.perf_counter() - bit_start_time
        time.sleep(max(0, period - latency))

    # Turn off all keys at the end of the transmission
    led_colors_off = [CorsairLedColor(id=key_id, r=0, g=0, b=0) for key_id in key_signal_mapping]
    sdk.set_led_colors(device_id, led_colors_off)

def send_binary_signals_with_CLK_and_SGL(binary_signals, data_ids, CLK_ids, SGL_ids, frequency):
    """
    Sends binary signals on transmission keys of a Corsair keyboard, assigning signals in
    groups of three to RGB channels (red, green, blue) for each key.

    Sends CLK signal on CLK keys at the specified frequency, toggling exactly once
    per bit (i.e. 180 degrees out of phase with the data lines).

    Sends SGL signal on SGL keys, switching high at the start of transmission and low
    at the end of transmission.

    Finally, ensures that CLK lines are turned off a half bit *after* SGL/data lines,
    to avoid accidental synchronous edges for the receiver.

    Parameters:
    - binary_signals (list or tuple): Binary signal strings (e.g. ['101100011', '101101100', ...]).
    - data_ids (list or tuple): Key IDs for the data signals.
    - CLK_ids (list or tuple): Key IDs for the clock signal(s).
    - SGL_ids (list or tuple): Key IDs for the SGL signal(s).
    - frequency (float): Frequency in Hz (data changes every 1/frequency).
    """
    import time

    # ─────────────────────────────────────────────────────────────────────────
    #  1) Basic Validation
    # ─────────────────────────────────────────────────────────────────────────
    if not binary_signals:
        print("No signals provided.")
        return

    # Ensure all signals have the same length
    signal_length = len(binary_signals[0])
    if not all(len(sig) == signal_length for sig in binary_signals):
        print("Error: All binary signals must be of equal length.")
        return

    # Check for overlaps in key sets
    data_set = set(data_ids)
    clk_set = set(CLK_ids)
    sgl_set = set(SGL_ids)

    overlap_data_clk = data_set.intersection(clk_set)
    overlap_data_sgl = data_set.intersection(sgl_set)
    overlap_clk_sgl = clk_set.intersection(sgl_set)

    errors = []
    if overlap_data_clk:
        errors.append(f"Data/CLK overlap: {overlap_data_clk}")
    if overlap_data_sgl:
        errors.append(f"Data/SGL overlap: {overlap_data_sgl}")
    if overlap_clk_sgl:
        errors.append(f"CLK/SGL overlap: {overlap_clk_sgl}")
    if errors:
        raise ValueError("Key overlap found: " + " | ".join(errors))

    # Ensure no duplicates in any individual list
    if len(data_set) != len(data_ids):
        print("Error: Duplicate key IDs in 'data_ids' are not allowed.")
        return
    if len(clk_set) != len(CLK_ids):
        print("Error: Duplicate key IDs in 'CLK_ids' are not allowed.")
        return
    if len(sgl_set) != len(SGL_ids):
        print("Error: Duplicate key IDs in 'SGL_ids' are not allowed.")
        return

    # Warn if there are more data keys than needed
    signals_per_key = 3
    needed_keys = (len(binary_signals) + signals_per_key - 1) // signals_per_key
    if needed_keys < len(data_ids):
        print(
            f"Warning: More data keys ({len(data_ids)}) than needed for {len(binary_signals)} signals. "
            f"Only the first {needed_keys} keys will actually receive signals."
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  2) Map signals to keys, 3 signals (R/G/B) per key
    # ─────────────────────────────────────────────────────────────────────────
    key_signal_mapping = {}
    for i, signal in enumerate(binary_signals):
        key_index = i // signals_per_key
        if key_index >= len(data_ids):
            break
        key = data_ids[key_index]
        if key not in key_signal_mapping:
            key_signal_mapping[key] = []
        key_signal_mapping[key].append(signal)

    # ─────────────────────────────────────────────────────────────────────────
    #  3) Set up the Corsair SDK
    # ─────────────────────────────────────────────────────────────────────────
    sdk, device_id, CorsairLedColor = keyboard_setup()

    # Define color map for each channel
    color_rgb = {
        'r': (255, 0, 0),
        'g': (0, 255, 0),
        'b': (0, 0, 255)
    }
    color_order = ['r', 'g', 'b']

    period = 1.0 / frequency
    half_period = period / 2.0

    # ─────────────────────────────────────────────────────────────────────────
    #  4) Turn SGL on (start of transmission)
    # ─────────────────────────────────────────────────────────────────────────
    sgl_on_color = (255, 255, 255)
    sgl_on_colors = [
        CorsairLedColor(id=s, r=sgl_on_color[0], g=sgl_on_color[1], b=sgl_on_color[2])
        for s in SGL_ids
    ]
    sdk.set_led_colors(device_id, sgl_on_colors)

    # Helper to build data LED colors for the current bit index
    def build_data_led_colors(bit_idx):
        data_colors = []
        for key_id, signals_for_key in key_signal_mapping.items():
            r, g, b = 0, 0, 0
            for signal_index, sig in enumerate(signals_for_key):
                if sig[bit_idx] == '1':
                    # channel is 'r', 'g', or 'b'
                    channel = color_order[signal_index % 3]
                    cr, cg, cb = color_rgb[channel]
                    r += cr
                    g += cg
                    b += cb
            # Clip to 255
            r, g, b = min(r, 255), min(g, 255), min(b, 255)
            data_colors.append(CorsairLedColor(id=key_id, r=r, g=g, b=b))
        return data_colors

    # Clock state: 0 (off) or 1 (on). Start with 0 (off).
    clock_state = 0

    def build_clk_led_colors(state):
        if state == 0:
            return [CorsairLedColor(id=c, r=0, g=0, b=0) for c in CLK_ids]
        else:
            return [CorsairLedColor(id=c, r=255, g=255, b=255) for c in CLK_ids]

    # ─────────────────────────────────────────────────────────────────────────
    #  5) Transmit signals bit by bit, toggling CLK once per bit
    # ─────────────────────────────────────────────────────────────────────────
    for bit_index in range(signal_length):
        start_time = time.perf_counter()

        data_colors = build_data_led_colors(bit_index)

        # First half: use current clock_state
        clk_colors_first_half = build_clk_led_colors(clock_state)
        colors_first_half = data_colors + clk_colors_first_half + sgl_on_colors
        sdk.set_led_colors(device_id, colors_first_half)
        time.sleep(half_period)

        # Toggle clock halfway
        clock_state = 1 - clock_state

        # Second half: use the new clock state
        clk_colors_second_half = build_clk_led_colors(clock_state)
        colors_second_half = data_colors + clk_colors_second_half + sgl_on_colors
        sdk.set_led_colors(device_id, colors_second_half)
        time.sleep(half_period)

        bit_duration = time.perf_counter() - start_time
        print(f"Bit #{bit_index + 1} displayed for {bit_duration:.6f} seconds")

    # ─────────────────────────────────────────────────────────────────────────
    #  6) Turn data & SGL off first
    # ─────────────────────────────────────────────────────────────────────────
    data_sgl_off = [CorsairLedColor(id=k, r=0, g=0, b=0) for k in key_signal_mapping.keys()]
    data_sgl_off += [CorsairLedColor(id=s, r=0, g=0, b=0) for s in SGL_ids]

    # We do NOT immediately turn off CLK lines, so if clock_state == 1, they remain on for now
    sdk.set_led_colors(device_id, data_sgl_off)
    # Add a half-bit margin to prevent the receiving end from seeing a simultaneous edge
    time.sleep(half_period)

    # ─────────────────────────────────────────────────────────────────────────
    #  7) Finally, turn CLK off
    # ─────────────────────────────────────────────────────────────────────────
    clk_off = [CorsairLedColor(id=c, r=0, g=0, b=0) for c in CLK_ids]
    sdk.set_led_colors(device_id, clk_off)