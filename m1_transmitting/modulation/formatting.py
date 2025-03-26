def parity_bit_calculation(sequence: str) -> int:
    if not all(bit in '01' for bit in sequence):
        raise ValueError("The input sequence must contain only '0' and '1'.")

    count_of_ones = sequence.count('1')
    return str(count_of_ones % 2)   

def rs232_format(message: str, idle_bits = 0):
    if not all(bit in '01' for bit in message):
        raise ValueError("The input message must contain only '0' and '1'.")
    
    parity_bit = parity_bit_calculation(message)
    return ('1' + message + parity_bit + '0'*idle_bits)

def frame_format(message: str, idle_bits = 0):
    # 1 + payload + 1 + idle_bits
    if not all(bit in '01' for bit in message):
        raise ValueError("The input message must contain only '0' and '1'.")

    else:
        return ('1' + message + '1' + '0'*idle_bits)
    
def FSK_format(binary_string: str, frequency_set: tuple):
    freq_0, freq_1 = frequency_set
    frequency_sequence = []
    for character in binary_string: 
        if character == '0':
            frequency_sequence.append(freq_0)
        elif character == '1':
            frequency_sequence.append(freq_1)
    return frequency_sequence

def MFSK_format(binary_string: str, frequency_set: tuple):
    import math

    n_frequencies = len(frequency_set)
    if n_frequencies & (n_frequencies - 1) != 0:
        raise ValueError("The number of frequencies must be a power of 2.")

    bits_per_segment = int(math.log2(n_frequencies))
    frequency_sequence = []

    for i in range(0, len(binary_string),  bits_per_segment):
        segment = binary_string[i:i+bits_per_segment]
        index = int(segment, 2)
        frequency_sequence.append(frequency_set[index])
    return frequency_sequence
