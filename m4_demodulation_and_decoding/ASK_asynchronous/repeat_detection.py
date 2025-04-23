def mark_bit_repeats(signal_csv_path, bit_rows, tolerance, consideration_bounds):
    import csv

    if bit_rows is None or tolerance is None:
        print("Error: bit_rows and tolerance must be specified.")
        return

    # Read the CSV file
    with open(signal_csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

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
            print(f"Error: Required column '{column}' is missing.")
            return
        elif count > 1:
            print(f"Error: Required column '{column}' is duplicated.")
            return

    # Get indices of required columns
    value_col_index = headers.index('Value')
    change_type_col_index = headers.index('Change Type')

    # Check for duplicates in other columns (print error but continue)
    other_columns = set(headers) - set(required_columns)
    for column in other_columns:
        if headers.count(column) > 1:
            print(f"Error: Column '{column}' is duplicated.")
            # Continue execution

    # Only consider rows within the consideration bounds
    start_row, end_row = consideration_bounds

    # Ensure start_row and end_row are within valid ranges
    start_row = max(2, start_row) - 1  # Start from row 1 to skip header
    end_row = min(len(rows), end_row) - 1

    # Check for repeats or potential repeats already marked in the area to be considered
    for i in range(start_row, end_row):
        change_type = rows[i][change_type_col_index].strip()
        if change_type == 'repeat' or change_type == 'potential repeat':
            print("Error: Repeats or potential repeats already marked in the consideration area.")
            return

    # Check if there are flips in the area to be considered
    flips_in_area = any(
        rows[i][change_type_col_index].strip() in ('up', 'down')
        for i in range(start_row, end_row)
    )
    if not flips_in_area:
        print("Warning: No flips found in the consideration area.")

    # Proceed with processing

    # Initialize variables
    bit_rows_current = round(bit_rows)
    rows_since_flip_or_repeat = 0
    rows_since_flip = 0
    current_repeat = 1
    potential_repeat_row_index = None
    after_potential_repeat_counter = None

    # Initialize list to store row numbers of flips
    flip_rows = []

    # Process rows consecutively
    i = start_row
    #print(f'Start Row: {start_row}')
    while i <= end_row:
        change_type = rows[i][change_type_col_index].strip()
        if change_type in ('up', 'down'):
            # Flip in current line
            rows_since_flip_or_repeat = 0
            rows_since_flip = 0
            current_repeat = 1
            potential_repeat_row_index = None
            after_potential_repeat_counter = None

            # Append the row number (1-based) to flip_rows
            flip_rows.append(i + 1)
        else:
            # No flip in current line
            rows_since_flip_or_repeat += 1
            rows_since_flip += 1

            if potential_repeat_row_index is not None:
                # Potential repeat has already been logged since last flip/repeat
                after_potential_repeat_counter += 1

                # Check if a flip has occurred within tolerance
                flip_found_within_tolerance = False
                lookahead_limit = min(i + tolerance, end_row)
                for j in range(i, lookahead_limit):
                    change_type_inner = rows[j][change_type_col_index].strip()
                    if change_type_inner in ('up', 'down'):
                        # Flip found within tolerance
                        flip_found_within_tolerance = True
                        break

                if flip_found_within_tolerance:
                    # Flip occurred within tolerance, reset counters and potential repeat markers
                    potential_repeat_row_index = None
                    after_potential_repeat_counter = None
                elif after_potential_repeat_counter >= tolerance:
                    # No flip occurred within tolerance
                    # CONFIRM A REPEAT
                    if rows[potential_repeat_row_index][change_type_col_index].strip() == 'potential repeat':
                        rows[potential_repeat_row_index][change_type_col_index] = 'repeat'
                    # Reset after confirming a repeat
                    current_repeat += 1
                    bit_rows_current = round(bit_rows * current_repeat) - rows_since_flip + 1
                    potential_repeat_row_index = None
                    after_potential_repeat_counter = None
                    rows_since_flip_or_repeat = 1

            else:
                # Potential repeat has not already been logged since last flip/repeat
                if rows_since_flip_or_repeat >= bit_rows_current:
                    # LOG POTENTIAL REPEAT
                    potential_repeat_row_index = i
                    if rows[potential_repeat_row_index][change_type_col_index].strip() == '':
                        rows[potential_repeat_row_index][change_type_col_index] = 'potential repeat'
                    # Reset after potential repeat
                    after_potential_repeat_counter = 0
                    #rows_since_flip_or_repeat = 0

        ## DEBUG STATEMENT ##
        # print(f'Change Type: {change_type}, Rows Since Flip: {rows_since_flip}, Current Repeat: {current_repeat}, Bit length before Next Repeat: {bit_rows_current}, '
        #       f'Rows since flip or repeat: {rows_since_flip_or_repeat}')
        i += 1  # Move to the next row

    # Save the modified data, overwriting the original file
    with open(signal_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    # Return the list of flip row numbers
    return flip_rows