import math
import time
from typing import List, Tuple
from cuesdk import CueSdk

from _SETUP_ import set_directory
set_directory()
import common.keyboard_interface as keyboard

def single_sine_wave(
    setup_items: list,
    key_IDs: List[int],
    frequency: float,
    T_symbol: int,
    colour: Tuple[int, int, int],
    samples_per_second: int = 60,
) -> None:
    """
    Transmits a single-frequency sine wave on the specified keys.

    Each RGB channel oscillates from 0 → max in a sine pattern:
      centre = max/2, amplitude = max/2.

    Args:
        setup_items (list): [sdk, device_id, CorsairLedColor] from keyboard_setup().
        key_IDs (List[int]): IDs of keys to animate.
        frequency (float): Wave frequency in Hz (must be > 0).
        T_symbol (int): Transmission duration in seconds (must be > 0).
        colour (Tuple[int,int,int]): Peak (R, G, B) values in [0..255].
        samples_per_second (int): Updates per second (higher = smoother).
    """
    # 1) Validate inputs
    if not key_IDs:
        print("single_sine_wave: no key_IDs provided.")
        return
    if frequency <= 0:
        print("single_sine_wave: frequency must be > 0.")
        return
    if T_symbol <= 0:
        print("single_sine_wave: T_symbol must be > 0.")
        return

    # 2) Sampling setup
    dt = 1.0 / samples_per_second
    total_samples = int(samples_per_second * T_symbol)

    # 3) Precompute centre & amplitude for each channel
    centres   = [c / 2.0 for c in colour]
    amplitudes = centres[:]  # each swings ±centre

    start_time = time.perf_counter()
    for i in range(total_samples):
        # time t = i * dt → angle = 2π·f·t
        angle = 2 * math.pi * frequency * (i * dt)

        # compute and clamp each channel
        rgb = []
        for ctr, amp in zip(centres, amplitudes):
            val = ctr + amp * math.sin(angle)
            rgb.append(max(0, min(255, int(round(val)))))

        # apply uniform colour across all keys
        result = keyboard.set_colour(setup_items, key_IDs, tuple(rgb))
        if result != 0:
            print(f"single_sine_wave: error setting colour {tuple(rgb)} (code={result})")

        # maintain real-time pacing
        elapsed = time.perf_counter() - start_time
        target  = (i + 1) * dt
        if (delay := target - elapsed) > 0:
            time.sleep(delay)

    print("single_sine_wave: complete.")

def multichannel_sine_waves(
    setup_items: list,
    key_IDs: List[int],
    R_frequency: float,
    G_frequency: float,
    B_frequency: float,
    T_symbol: float,
    samples_per_second: int = 60,
) -> None:
    """
    Transmits independent sine waves on the R, G, and B channels.

    Each channel oscillates from 0 → 255 in a sine pattern:
      centre = 127.5, amplitude = 127.5.

    Args:
        setup_items (list): [sdk, device_id, CorsairLedColor] from keyboard_setup().
        key_IDs (List[int]): IDs of keys to animate.
        R_frequency (float): Red-channel frequency in Hz (must be > 0).
        G_frequency (float): Green-channel frequency in Hz (must be > 0).
        B_frequency (float): Blue-channel frequency in Hz (must be > 0).
        T_symbol (float): Total transmission duration in seconds (must be > 0).
        samples_per_second (int): Updates per second (higher = smoother).
    """
    # 1) Validate inputs
    if not key_IDs:
        print("multichannel_sine_waves: no key_IDs provided.")
        return
    if R_frequency <= 0 or G_frequency <= 0 or B_frequency <= 0:
        print("multichannel_sine_waves: all frequencies must be > 0.")
        return
    if T_symbol <= 0:
        print("multichannel_sine_waves: T_symbol must be > 0.")
        return

    # 2) Sampling configuration
    dt = 1.0 / samples_per_second
    total_samples = int(samples_per_second * T_symbol)

    # 3) Precompute centre & amplitude (127.5 each)
    centre = 255.0 / 2.0
    amplitude = centre

    start_time = time.perf_counter()
    for i in range(total_samples):
        t = i * dt
        # per-channel angles
        angle_r = 2 * math.pi * R_frequency * t
        angle_g = 2 * math.pi * G_frequency * t
        angle_b = 2 * math.pi * B_frequency * t

        # compute and clamp each channel
        r = int(round(centre + amplitude * math.sin(angle_r)))
        g = int(round(centre + amplitude * math.sin(angle_g)))
        b = int(round(centre + amplitude * math.sin(angle_b)))
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

        # apply color to all keys
        result = keyboard.set_colour(setup_items, key_IDs, (r, g, b))
        if result != 0:
            print(f"multichannel_sine_waves: error setting colour ({r},{g},{b}) (code={result})")

        # maintain timing
        elapsed = time.perf_counter() - start_time
        target  = (i + 1) * dt
        if (delay := target - elapsed) > 0:
            time.sleep(delay)

    print("multichannel_sine_waves: complete.")