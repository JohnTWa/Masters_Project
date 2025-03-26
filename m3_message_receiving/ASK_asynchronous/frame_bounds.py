import csv

def determine_frame_bounds(signal_csv, idle_rows, start_n, consideration_bounds, mark=False):
    """
    Determines signal bounds in a signal CSV file based on idle zones and flips.
    
    Parameters:
    - signal_csv (str): Path to the CSV file containing signal data.
    - idle_rows (int): Number of rows without a flip to qualify as an idle zone.
    - start_n (int): Starting number for signal numbering.
    - consideration_bounds (tuple): Tuple containing the start and end row numbers to consider.
    - mark (bool): Whether to mark the signal bounds in the CSV file (default is False).
    
    Returns:
    - tuple: A tuple containing frame bounds and the highest signal number reached.
    """
    try:
        # Read the CSV file
        with open(signal_csv, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return (), start_n - 1

    # Check for required headers
    required_headers = ['Value', 'Change Type']
    for req_header in required_headers:
        count = header.count(req_header)
        if count == 0:
            print(f"Error: Required column header '{req_header}' is missing.")
            return (), start_n - 1
        elif count > 1:
            print(f"Error: Required column header '{req_header}' is repeated.")
            return (), start_n - 1

    # Identify indices of required columns
    value_col_index = header.index('Value')
    change_type_col_index = header.index('Change Type')

    # Check for duplicates in other columns
    other_headers = set(header) - set(required_headers)
    for col in other_headers:
        if header.count(col) > 1:
            print(f"Error: Column header '{col}' is duplicated.")
            # Print error but carry on

    # Only consider rows within the consideration bounds
    start_row, end_row = consideration_bounds
    start_index = max(2, start_row) - 2  # data starts from index 0
    end_index = min(len(rows) + 1, end_row) - 2  # data starts from index 0

    if start_index > end_index or start_index >= len(rows):
        print("Warning: No data in the consideration bounds.")
        return (), start_n - 1

    data_rows = rows[start_index:end_index + 1]

    # Initialize variables
    signal_bounds = []
    signal_number = start_n - 1
    last_flip_idx = None
    last_flip_type = None
    idle_start = 0
    signal_start = None

    # Add 'signal Bounds' column if marking is enabled
    if mark:
        if 'Signal Bounds' not in header:
            header.append('Signal Bounds')
            for row in rows:
                row.append('')
        signal_bounds_col_index = header.index('Signal Bounds')

    for idx, row in enumerate(data_rows):
        global_idx = idx + start_index
        change_type = row[change_type_col_index].strip().lower()

        if change_type in ["up", "down"]:
            # If the first flip is an 'up' and follows an idle zone (including at the start of bounds)
            if signal_start is None and change_type == "up" and (idx - idle_start >= idle_rows or idx == 0):
                signal_start = global_idx + 2
                signal_number += 1
            elif signal_start is not None and change_type == "down":
                # Check if this is followed by an idle zone to mark the signal end
                for future_idx in range(idx + 1, len(data_rows)):
                    if data_rows[future_idx][change_type_col_index].strip().lower() in ["up", "down"]:
                        break
                    if future_idx - idx >= idle_rows:
                        signal_end = global_idx + 2
                        signal_bounds.append((signal_start, signal_end))
                        if mark:
                            rows[signal_start - 2][-1] = f"signal{signal_number}_start"
                            rows[signal_end - 2][-1] = f"signal{signal_number}_end"
                        signal_start = None
                        break

    # Handle the case where a signal is open at the end of the consideration bounds
    if signal_start is not None:
        last_down_flip_idx = None
        for rev_idx in range(len(data_rows) - 1, -1, -1):
            if data_rows[rev_idx][change_type_col_index].strip().lower() == "down":
                last_down_flip_idx = rev_idx + start_index + 2
                break
        if last_down_flip_idx is not None:
            signal_bounds.append((signal_start, last_down_flip_idx))
            if mark:
                rows[signal_start - 2][-1] = f"signal{signal_number}_start"
                rows[last_down_flip_idx - 2][-1] = f"signal{signal_number}_end"

    # Save marked CSV if required
    if mark:
        with open(signal_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

    print(f"Found {len(signal_bounds)} signal(s).")
    return tuple(signal_bounds), signal_number