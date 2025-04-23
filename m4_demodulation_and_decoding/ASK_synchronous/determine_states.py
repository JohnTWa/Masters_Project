import csv

def determine_states(levels_and_events_csv_path, rows_to_sample, consideration_bounds=None):
    """
    Reads a CSV containing light levels over time and determines states at specified rows based on the most recent 'up'/'down' change.
    Adds a 'State' column to the CSV with the results.

    Parameters:
    - levels_and_events_csv_path (str): Path to the CSV.
    - rows_to_sample (list): Row indexes in the CSV to determine states for.
    - consideration_bounds (tuple, optional): (start_row, end_row) to limit change detection scope.

    Returns:
    - bit_sequence (str): Binary string of states for valid rows_to_sample.
    """
    # Read CSV into memory
    with open(levels_and_events_csv_path, 'r') as f:
        csv_rows = list(csv.reader(f))
    
    # Error: No 'Change Type' column
    header = csv_rows[0] if csv_rows else []
    if 'Change Type' not in header:
        print("Error: 'Change Type' column not found.")
        return ""
    change_type_col = header.index('Change Type')
    
    # Validate consideration_bounds
    if consideration_bounds:
        start, end = consideration_bounds
        if start < 0 or end >= len(csv_rows) or start > end:
            print("Error: Invalid consideration_bounds.")
            return ""
    
    # Check for empty rows_to_sample
    if not rows_to_sample:
        print("Warning: No rows to sample.")
        return ""
    
    # Filter valid rows_to_sample
    valid_rows = []
    for row in rows_to_sample:
        if 0 <= row < len(csv_rows):
            if not consideration_bounds or (start <= row <= end):
                valid_rows.append(row)
    
    if not valid_rows:
        print("Note: All rows_to_sample are invalid or outside consideration_bounds.")
        return ""
    
    # Check if there are any changes in consideration bounds
    has_changes = False
    if consideration_bounds:
        start, end = consideration_bounds
        for row in csv_rows[start:end+1]:
            if row[change_type_col].strip().lower() in ('up', 'down'):
                has_changes = True
                break
    else:
        for row in csv_rows[1:]:  # Skip header
            if row[change_type_col].strip().lower() in ('up', 'down'):
                has_changes = True
                break
    
    if not has_changes:
        print("Note: No 'up'/'down' changes in consideration bounds.")
    
    # Add 'State' column if missing
    if 'State' not in header:
        header.append('State')
        for row in csv_rows[1:]:
            row.append('')
    
    state_col = header.index('State')
    bit_sequence = []
    
    # Determine states for each valid row
    for row_idx in valid_rows:
        current_row = csv_rows[row_idx]
        state = '0'  # Default
        
        # Determine search bounds
        search_start = 0
        search_end = row_idx
        if consideration_bounds:
            search_start = max(search_start, start)
            search_end = min(search_end, end)
        
        # Find most recent change
        for i in range(search_end, search_start-1, -1):
            change = csv_rows[i][change_type_col].strip().lower()
            if change == 'up':
                state = '1'
                break
            elif change == 'down':
                state = '0'
                break
        
        # Update CSV row and bit sequence
        current_row[state_col] = state
        bit_sequence.append(state)
    
    # Write updated CSV
    with open(levels_and_events_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    
    return ''.join(bit_sequence)