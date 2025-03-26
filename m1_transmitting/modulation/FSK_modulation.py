import math
import time
from typing import List, Tuple
from cuesdk import CueSdk

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

def transmit_sine_wave(
    sdk, 
    device_id: str,
    CorsairLedColor,
    data_keys: List[int],
    frequency: float,
    periods: int,
    colour: Tuple[int, int, int],
    SAMPLES_PER_PERIOD: int = 60,
):
    """
    Transmits a sine wave on all given data keys at the specified frequency for the given
    number of periods. Each color channel is centered around half its maximum with amplitude
    equal to half, so it varies from 0 up to its maximum in a sinusoidal manner.

    Parameters:
        data_keys (list of int): Key IDs to transmit the sine wave on.
        frequency (float): Frequency (in Hz) of the sine wave.
        periods (int): Number of wave periods to transmit before finishing.
        colour (tuple): (R, G, B) maximum color values (0..255).
        SAMPLES_PER_PERIOD (int): Number of steps to update per period (higher = smoother).
    """
    # 1) Basic validation
    if not data_keys:
        print("No data keys provided.")
        return
    if frequency <= 0:
        print("Frequency must be > 0.")
        return
    if periods < 1:
        print("Periods must be at least 1.")
        return

    # 2) Calculate total time and step duration
    total_period_time = 1.0 / frequency  # length of one period in seconds
    total_wave_time = periods * total_period_time  # how long to run in total
    dt = total_period_time / SAMPLES_PER_PERIOD  # time step per update

    # 3) Calculate center & amplitude per color channel
    #    So the wave goes from 0 to color[channel].
    #    e.g. for R=255 => center=127, amplitude=127
    r_center = colour[0] / 2.0
    r_amp = r_center
    g_center = colour[1] / 2.0
    g_amp = g_center
    b_center = colour[2] / 2.0
    b_amp = b_center

    # 4) Main loop: step through the total number of samples
    total_samples = periods * SAMPLES_PER_PERIOD

    start_time = time.perf_counter()
    for sample_index in range(total_samples):
        # Fraction of the current wave cycle
        # sample_index goes from 0 .. total_samples-1
        # wave_phase from 0 .. periods
        wave_phase = float(sample_index) / float(SAMPLES_PER_PERIOD)  # wave # within [0..periods)
        angle = 2.0 * math.pi * wave_phase  # one full sine wave per period

        # Compute each channel’s instantaneous value
        r_val = r_center + r_amp * math.sin(angle)
        g_val = g_center + g_amp * math.sin(angle)
        b_val = b_center + b_amp * math.sin(angle)

        # Clamp and round to ensure valid [0..255] integers
        r_clamped = max(0, min(255, int(round(r_val))))
        g_clamped = max(0, min(255, int(round(g_val))))
        b_clamped = max(0, min(255, int(round(b_val))))

        # Build the color array for all data keys
        led_colors = [
            CorsairLedColor(id=key_id, r=r_clamped, g=g_clamped, b=b_clamped)
            for key_id in data_keys
        ]

        # Set the color on all data keys
        result = sdk.set_led_colors(device_id, led_colors)
        if result != 0:
            print(f"Failed to set LED colors (error={result})")

        # Sleep until the next sample
        # Adjust to keep consistent timing if necessary
        elapsed = time.perf_counter() - start_time
        target_time = (sample_index + 1) * dt
        remaining = target_time - elapsed
        if remaining > 0:
            time.sleep(remaining)

    # 5) End of wave transmission
    #    (Optionally, you could turn the keys off or do something else here)
    print("Sine wave transmission complete.")

def transmit_triangle_wave(
    data_keys: List[int],
    frequency: float,
    periods: int,
    colour: Tuple[int, int, int],
    SAMPLES_PER_PERIOD: int = 50
):
    """
    Transmits a triangle wave on all given data keys at the specified frequency for the given
    number of periods. For each channel in 'colour', the wave starts at 0, rises linearly to
    the channel's max, then falls linearly back to 0 in one period.

    Parameters:
        data_keys (list of int): Key IDs to transmit the triangle wave on.
        frequency (float): Frequency (in Hz) of the triangle wave.
        periods (int): Number of wave periods to transmit before finishing.
        colour (tuple): (R, G, B) maximum color values (0..255).
        SAMPLES_PER_PERIOD (int): Number of steps to update per period (higher = smoother).
    """
    # 1) Basic validation
    if not data_keys:
        print("No data keys provided.")
        return
    if frequency <= 0:
        print("Frequency must be > 0.")
        return
    if periods < 1:
        print("Periods must be at least 1.")
        return

    # 2) Calculate total time for one period and the step duration
    period_time = 1.0 / frequency  # seconds per period
    total_wave_time = periods * period_time
    dt = period_time / SAMPLES_PER_PERIOD

    # 3) Initialize the iCUE SDK objects
    #    (Adjust these lines to match your actual setup/environment)
    sdk, device_id, CorsairLedColor = keyboard_setup()

    # 4) Main loop: time-step through the total number of samples
    total_samples = periods * SAMPLES_PER_PERIOD
    start_time = time.perf_counter()

    for sample_index in range(total_samples):
        # wave_phase => how many "periods" have elapsed so far (fraction)
        # e.g. goes from 0 up to (periods - a tiny fraction).
        wave_phase = float(sample_index) / float(SAMPLES_PER_PERIOD)
        # frac is the fractional part within the current period [0..1)
        frac = wave_phase - math.floor(wave_phase)

        # Triangle formula: tri in [0..1..0]
        # tri = 1 - abs(2*frac - 1)
        # This yields 0 -> 1 -> 0 over one period
        tri_value = 1.0 - abs(2.0 * frac - 1.0)

        # Compute each channel’s instantaneous color
        r_val = colour[0] * tri_value
        g_val = colour[1] * tri_value
        b_val = colour[2] * tri_value

        # Convert to integers
        r_clamped = max(0, min(255, int(round(r_val))))
        g_clamped = max(0, min(255, int(round(g_val))))
        b_clamped = max(0, min(255, int(round(b_val))))

        # Build the color array for all data keys
        led_colors = [
            CorsairLedColor(id=key_id, r=r_clamped, g=g_clamped, b=b_clamped)
            for key_id in data_keys
        ]

        # Send the color update
        result = sdk.set_led_colors(device_id, led_colors)
        if result != 0:
            print(f"Failed to set LED colors (error={result})")

        # Sleep until the next sample
        elapsed = time.perf_counter() - start_time
        target_time = (sample_index + 1) * dt
        remaining = target_time - elapsed
        if remaining > 0:
            time.sleep(remaining)

    # 5) Done transmitting the wave
    print("Triangle wave transmission complete.")
    # (Optionally turn off keys here or leave them at final value)