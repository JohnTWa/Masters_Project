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