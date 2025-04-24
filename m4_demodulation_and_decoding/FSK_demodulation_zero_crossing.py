from _SETUP_ import set_directory
set_directory()

import math
import heapq

from m4_demodulation_and_decoding.FSK.zero_crossing import zero_crossing_count

## Define Filepaths ##
rgb_csv_path = 'files/spreadsheets/s5_rgb_normalised.csv'

## Define signal parameters ##
bits_per_frame      = 8    # total bits in one frame
T_symbol            = 2    # duration of one symbol, in seconds
frequency_set       = (0.5, 1.0, 1.5, 2.0)
camera_sample_rate  = 60   # frames per second
signal_start_row    = 0

# Derived parameters for M-FSK
M                   = len(frequency_set)
bits_per_symbol     = int(math.log2(M))                  # here log2(4)=2
symbols_per_frame   = bits_per_frame // bits_per_symbol  # 8/2 = 4 symbols
samples_per_symbol  = int(camera_sample_rate * T_symbol)

frame_bits = ''

for sym in range(symbols_per_frame):
    start_row = signal_start_row + sym * samples_per_symbol
    end_row   = start_row + samples_per_symbol
    print(f"Symbol {sym}: rows {start_row}–{end_row-1}")

    # count zero crossings in the green channel (column=1, say)
    zero_crossings = zero_crossing_count(
        rgb_csv_path,
        column=2,
        consideration_bounds=(start_row, end_row - 10),
        sampling_rate=camera_sample_rate
    )

    # estimate the frequency
    freq_est = zero_crossings / (2 * T_symbol)
    # pick the closest tone in our set
    tone = min(frequency_set, key=lambda f: abs(f - freq_est))
    symbol_index = frequency_set.index(tone)

    # convert symbol index to a 2-bit string, zero-padded
    bits = format(symbol_index, f'0{bits_per_symbol}b')
    frame_bits += bits

    print(f"  est. {freq_est:.2f} Hz → tone {tone} Hz → symbol {symbol_index} → bits '{bits}'")

print(f"Recovered frame bits: {frame_bits}")