def is_power_of_two(n):
    """
    Checks if a number is a power of two.
    """

    return (n != 0) and ((n & (n - 1)) == 0)  

def hamming_encode(data):
    """
    Encodes the input binary data using Hamming code.

    Parameters:
    data (str): A string representing binary data (e.g., '1011').

    Returns:
    str: The Hamming-encoded binary codeword.
    """
    # Convert data to a list for easier manipulation
    data_bits = list(data)
    m = len(data_bits)
    
    # Calculate the number of parity bits needed
    r = 1
    while (2 ** r) < (m + r + 1):
        r += 1
    
    # Total length of codeword
    total_length = m + r
    
    # Initialize codeword with placeholders for parity bits
    codeword = ['0'] * (total_length + 1)  # 1-based indexing
    
    # Insert data bits into the codeword
    j = 0  # Index for data_bits
    for i in range(1, total_length + 1):
        if not is_power_of_two(i):
            codeword[i] = data_bits[j]
            j += 1
    
    # Calculate parity bits
    for i in range(r):
        parity_pos = 2 ** i
        parity = 0
        for j in range(1, total_length + 1):
            if j & parity_pos and j != parity_pos:
                parity ^= int(codeword[j])
        codeword[parity_pos] = str(parity)
    
    # Convert the codeword list back to a string, excluding index 0
    return ''.join(codeword[1:])

def hamming_decode(codeword):
    """
    Decodes a Hamming-encoded binary string and returns the payload.
    If an uncorrectable error is detected, prints an error message and continues.

    Parameters:
    codeword (str): A string of '0's and '1's representing the Hamming codeword.

    Returns:
    str: The decoded payload as a binary string.
    """
    # Convert codeword to list for easier manipulation (1-based indexing)
    cw = list(codeword)
    n = len(cw)
    
    # Determine the number of parity bits p
    p = 0
    while (2 ** p) < (n + 1):
        p += 1
    
    # Calculate the error position
    error_pos = 0
    for i in range(p):
        parity_pos = 2 ** i
        parity = 0
        j = parity_pos - 1  # Convert to 0-based index
        while j < n:
            # Toggle bits in the range [j, j + parity_pos)
            for k in range(j, min(j + parity_pos, n)):
                parity ^= int(cw[k])
            j += 2 * parity_pos
        # Compare with the parity bit in the codeword
        if parity != 0:
            error_pos += parity_pos
    
    # If there is an error, attempt to correct it
    if error_pos != 0:
        if error_pos <= n:
            # Flip the erroneous bit
            corrected_bit = '1' if cw[error_pos - 1] == '0' else '0'
            cw[error_pos - 1] = corrected_bit
            print(f"Single-bit error detected and corrected at position {error_pos}.")
        else:
            # Uncorrectable error detected
            print("Uncorrectable error detected: Error position exceeds codeword length. Possible multiple bit errors.")
            # Optionally, you can choose to return None or the uncorrected payload
            # Here, we'll proceed to extract the payload without correction
    
    # Extract the payload by removing parity bits
    payload = []
    for i in range(1, n + 1):
        if not is_power_of_two(i):
            payload.append(cw[i - 1])
    
    return ''.join(payload)