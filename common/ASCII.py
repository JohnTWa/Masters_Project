# Example of encoding a text using ASCII
def text_to_ascii(text):

    ascii_codes = []
    for char in text:
        ascii_code = ord(char)
        if ascii_code > 127:
            raise ValueError(f"Character '{char}' cannot be encoded in ASCII.")
        else:
            ascii_codes.append(ascii_code)

    return ascii_codes

def numbers_to_7_bit_binary(numbers):

    binary_codes = []

    for number in numbers: 
        binary_string = format(number, '07b') # Converts to 7 bit binary string
        binary_codes.append(binary_string)

    return binary_codes

def file_to_ascii_binary(file_path):

    try:
        with open(file_path, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} does not exist.")
    
    # Use the existing function to convert the text to ASCII binary
    ascii_codes =  text_to_ascii(text)
    return numbers_to_7_bit_binary(ascii_codes)

def list_splitting(data, number):

    if not isinstance(data, (list, tuple)):
        raise TypeError("Input must be a list or tuple.")
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Number must be a positive integer.")

    # Split the list/tuple into chunks
    chunks = [data[i:i+number] for i in range(0, len(data), number)]

    # Return in the same type as the input
    return tuple(chunks) if isinstance(data, tuple) else chunks

def list_splitting_reordered(data, number):

    if not isinstance(data, (list, tuple)):
        raise TypeError("Input must be a list or tuple.")
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Number must be a positive integer.")

    # Initialize buckets for each key
    buckets = [[] for _ in range(number)]

    # Distribute messages across keys cyclically
    for i, message in enumerate(data):
        buckets[i % number].append(message)

    # Convert to tuple of tuples (to match the input type if it was a tuple)
    return tuple(map(tuple, buckets)) if isinstance(data, tuple) else [tuple(bucket) for bucket in buckets]

def pad_signals(signal_sets, pad_signal='0000000', pad_count=3):
    """
    Pads each signal in the list with a specified number of pad signals.

    Args:
        signal_sets (list or tuple): The original list of signals (e.g., ['message1', 'message2', ...]).
        pad_signal (str): The signal used for padding (default is '0000000').
        pad_count (int): The number of padding signals to add after each original signal (default is 3).

    Returns:
        list: A new list with the original signals and their corresponding padding.
    """
    padded_list = []
    for signal in signal_sets:
        padded_list.append(signal)  # Add the original signal
        padded_list.extend([pad_signal] * pad_count)  # Add padding signals
    return padded_list

def insert_padding(data_list, pad_signal, count, index):
    """
    Inserts a specified padding signal a given number of times at a specific index in a list.

    Args:
        data_list (list): The original list of items.
        pad_signal (any): The signal to use for padding.
        count (int): The number of times to insert the padding signal.
        index (int): The index at which to insert the padding.

    Returns:
        list: A new list with the padding inserted.

    Raises:
        TypeError: If data_list is not a list.
        ValueError: If count is not a non-negative integer or index is out of range.
    """
    if not isinstance(data_list, list):
        raise TypeError("data_list must be a list.")
    if not isinstance(count, int) or count < 0:
        raise ValueError("count must be a non-negative integer.")
    if not isinstance(index, int) or index < 0 or index > len(data_list):
        raise ValueError("index must be within the valid range of the list.")

    # Create the padding as a list
    padding = [pad_signal] * count

    # Insert padding into the list
    return data_list[:index] + padding + data_list[index:]

def binary_to_ascii(binary_str):
    """
    Converts a 7-bit ASCII binary string to the corresponding ASCII character.

    Parameters:
    - binary_str (str): A 7-bit binary string (e.g., "1000001").

    Returns:
    - str: The corresponding ASCII character or an error message if the input is invalid.
    """
    # Validate input
    if len(binary_str) != 7 or not all(bit in '01' for bit in binary_str):
        return "Error: Input must be a 7-bit binary string."
    
    # Convert binary string to decimal
    decimal_value = int(binary_str, 2)
    
    # Convert decimal to ASCII character
    ascii_char = chr(decimal_value)
    
    return ascii_char