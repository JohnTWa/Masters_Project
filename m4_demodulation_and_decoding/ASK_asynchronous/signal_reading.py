import csv
import string

def read_signal(signal_csv_path, consideration_bounds, start_bits=0, end_bits=0, bits=8, crop=False):

    # Read the CSV file
    with open(signal_csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Check if the CSV has data
    if len(rows) <= 1:
        print("No data found in the specified CSV.")
        return

    # Get headers
    headers = rows[0]

    # Required columns
    required_columns = ['Value', 'Change Type']

    # Check for missing required columns and duplicates
    for column in required_columns:
        count = headers.count(column)
        if count == 0:
            print(f"signal Decoding Error: Required column '{column}' is missing.")
            return
        elif count > 1:
            print(f"signal Decoding Error: Required column '{column}' is duplicated.")
            return

    # Get indices of required columns
    value_col_index = headers.index('Value')
    change_type_col_index = headers.index('Change Type')

    # Check for duplicates in other columns (print error but continue)
    other_columns = set(headers) - set(required_columns)
    for column in other_columns:
        if headers.count(column) > 1:
            print(f"signal Decoding Error: Column '{column}' is duplicated.")
            # Continue execution

    # Only consider rows within the consideration bounds
    start_row, end_row = consideration_bounds

    # Adjust for zero-based indexing (rows list starts from index 0)
    # Subtract 1 from start_row and end_row since the header is at index 0
    start_row = max(2, start_row) - 1  # Ensure start_row is at least 1 to skip header
    end_row = min(len(rows) - 1, end_row) - 1  # Adjust end_row

    # Extract the relevant rows
    data_rows = rows[start_row:end_row+1]

    # Initialize variables
    binary_string = ''
    state = None  # Will be set to '1' or '0' based on flips
    previous_flip = None
    first_row = True
    flips_found = False

    # Process each row
    for idx, row in enumerate(data_rows):
        change_type = row[change_type_col_index].strip()

        # Check for repeats of 'up' or 'down' flips
        if change_type == 'up' or change_type == 'down':
            flips_found = True
            if previous_flip == change_type:
                print(f"signal Decoding Error between rows {start_row + idx + 1} and {start_row + idx + 2}: Two '{change_type}' flips follow each other.")
                return
            previous_flip = change_type

            # Set the state
            if change_type == 'up':
                state = '1'
            elif change_type == 'down':
                state = '0'

            # Append the state to the binary string
            binary_string += state
            first_row = False

        elif change_type == 'repeat':
            if first_row:
                print(f"signal Decoding Error at row {start_row + idx + 1}: The first change type is 'repeat'.")
                return
            if state is None:
                print(f"signal Decoding Error at row {start_row + idx + 1}: State is undefined before 'repeat'.")
                return
            # Append the current state to the binary string
            binary_string += state

        elif change_type == 'potential repeat':
            # Ignore potential repeats
            pass
        elif change_type == '':
            # Do nothing
            pass
        else:
            # Handle unknown change types
            print(f"Warning at row {start_row + idx + 1}: Unknown change type '{change_type}'. Ignoring.")
            pass

    # Check for flips
    if not flips_found:
        print(f"signal Decoding Error between rows {start_row + 1} and {end_row + 1}: No flips found.")
        # Continue execution (return the binary string if applicable)

    # Remove start_bits from the beginning
    binary_string = binary_string[start_bits:]

    # Remove trailing zeros if the string is longer than bits + end_bits and ends with '0'
    while len(binary_string) > bits + end_bits and binary_string.endswith('0'):
        binary_string = binary_string[:-1]
        # Stop removing if the last bit is '1' or length is equal to bits + end_bits
        if binary_string.endswith('1') or len(binary_string) == bits + end_bits:
            break

    # Remove end_bits from the end
    if end_bits > 0:
        binary_string = binary_string[:-end_bits]

    # Crop the string if necessary
    final_length = len(binary_string)
    if crop and final_length > bits:
        # Remove bits from the end to make the string length equal to 'bits'
        binary_string = binary_string[:bits]
        final_length = bits

    # Check for length issues
    if final_length < bits:
        print(f"signal Decoding Error: The length of the final string ({final_length}) is less than 'bits' ({bits}).")
        # Continue execution
    elif final_length > bits:
        print(f"signal Decoding Error: The length of the final string ({final_length}) is more than 'bits' ({bits}).")
        # Continue execution

    # Return the binary string
    return binary_string