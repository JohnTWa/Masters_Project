import csv

def detect_edges(rgb_csv_path, column_number, levels_and_events_csv_path, threshold_fraction=0.1, consideration_bounds=None):
    """
    Reads a specified RGB column from a CSV, detects up/down flips, outputs a debugging CSV with flip markers,
    and returns the row indexes of the debugging CSV where flips are annotated.

    Parameters:
    - rgb_csv_path (str): Path to the input CSV containing RGB values.
    - column_number (int): The column index to read values from (0-indexed).
    - levels_and_events_csv_path (str): Path to the output debugging CSV file.
    - threshold_fraction (float): Fraction of the value range to use as a change threshold.
    - consideration_bounds (tuple, optional): A tuple (start_row, end_row) specifying the range of rows to consider 
      (0-indexed, inclusive). Defaults to None.

    Returns:
    - state_change_rows (list): List of row indexes in the debugging CSV where flips are annotated.
    """
    # Read the input CSV and extract the specified column
    values = []
    with open(rgb_csv_path, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                values.append(float(row[column_number]))
            except ValueError:
                continue  # Skip invalid rows

    # Apply consideration_bounds if provided
    if consideration_bounds is not None:
        start_row, end_row = consideration_bounds
        # Convert bounds to a slice (e.g., [start:end+1] for inclusive slicing)
        slice_start = start_row if start_row is not None else 0
        slice_end = (end_row + 1) if end_row is not None else None
        values = values[slice_start:slice_end]

    if not values:
        print("No data found in the specified range.")
        return []

    # Calculate threshold
    value_range = max(values) - min(values)
    threshold = value_range * threshold_fraction

    # Detect flips and track annotated rows in the debug CSV
    debug_data = [("Value", "Change Type")]
    previous_value = values[0]
    current_state = 0
    flip_count = 0
    state_change_rows = []

    for i in range(1, len(values)):
        change = values[i] - previous_value
        if abs(change) > threshold:
            if change > 0 and current_state == 0:
                # Up flip
                current_state = 1
                debug_data.append((values[i], "up"))
                flip_count += 1
                state_change_rows.append(len(debug_data) - 1)  # Track debug CSV row index
            elif change < 0 and current_state == 1:
                # Down flip
                current_state = 0
                debug_data.append((values[i], "down"))
                flip_count += 1
                state_change_rows.append(len(debug_data) - 1)
        else:
            debug_data.append((values[i], ""))
        previous_value = values[i]

    # Save the debugging CSV
    with open(levels_and_events_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(debug_data)

    print(f"Debugging CSV saved to {levels_and_events_csv_path}")
    print(f"Number of flips detected: {flip_count}")

    return state_change_rows

import csv

def detect_edges_with_orig_index(
    rgb_csv_path,
    column_number,
    levels_and_events_csv_path,
    threshold_fraction=0.1,
    consideration_bounds=None
):
    """
    Reads a specified RGB column from a CSV, detects up/down flips, and outputs a debugging CSV
    that includes original frame index, value, and change type. Returns a list of original frame
    indices where flips occur.

    Parameters:
    - rgb_csv_path (str): Path to the input CSV containing RGB values (one row per video frame).
    - column_number (int): The column index to read values from (0-indexed).
    - levels_and_events_csv_path (str): Path to the output debugging CSV file.
    - threshold_fraction (float): Fraction of the value range to use as a change threshold.
    - consideration_bounds (tuple, optional): (start_row, end_row) specifying a slice of frames
      to consider (0-indexed, inclusive). If None, considers all frames.

    Returns:
    - flip_frames (list of int): The original frame indices at which flips (up or down) are detected.
    """

    # 1) Read the input CSV and extract (frame_index, value) for the specified column
    all_values = []  # will store (frame_index, float_value)

    with open(rgb_csv_path, mode='r') as infile:
        reader = csv.reader(infile)
        row_index = -1
        for row in reader:
            row_index += 1
            # Try to parse the column_number-th entry in this row
            try:
                val = float(row[column_number])
            except (ValueError, IndexError):
                # Skip rows that are invalid or don't have this column
                continue
            all_values.append((row_index, val))

    # 2) Apply consideration_bounds if provided
    #    We'll keep the original row_index, but slice the array of (frame_idx, val).
    if consideration_bounds is not None:
        start_row, end_row = consideration_bounds  # inclusive
        # Filter to keep only those whose frame_index is in [start_row, end_row]
        if start_row is None:
            start_row = 0
        # end_row could be None => meaning "no upper limit"
        filtered = []
        for (fidx, val) in all_values:
            if fidx < start_row:
                continue
            if (end_row is not None) and (fidx > end_row):
                break
            filtered.append((fidx, val))
        all_values = filtered

    if not all_values:
        print("No valid data found in the specified range/column.")
        # Write a minimal CSV with only a header
        with open(levels_and_events_csv_path, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Frame Index", "Value", "Change Type"])
        return []

    # 3) Calculate threshold
    values_only = [v for _, v in all_values]
    val_min, val_max = min(values_only), max(values_only)
    value_range = val_max - val_min
    threshold = value_range * threshold_fraction

    # 4) Detect flips, track them, and build debugging data
    #    We store in debug_data one line per row in all_values (so it's 1:1 with frames after parse).
    debug_data = [("Frame Index", "Value", "Change Type")]

    # Track "state" (like your original function, 0 vs 1) and "previous_value"
    # Start from the first row as your baseline
    prev_frame_idx, prev_value = all_values[0]
    current_state = 0  # e.g., assume 'off' initially
    flip_frames = []

    # Include the first row in debug_data (no change yet)
    debug_data.append((prev_frame_idx, prev_value, ""))

    for i in range(1, len(all_values)):
        frame_idx, current_val = all_values[i]
        change = current_val - prev_value

        if abs(change) > threshold:
            # Evaluate if up or down flip
            if change > 0 and current_state == 0:
                current_state = 1
                debug_data.append((frame_idx, current_val, "up"))
                flip_frames.append(frame_idx)
            elif change < 0 and current_state == 1:
                current_state = 0
                debug_data.append((frame_idx, current_val, "down"))
                flip_frames.append(frame_idx)
            else:
                # It's a change that doesn't produce a flip in 0->1 or 1->0 sense
                # or we ignore if we're already in the same state
                debug_data.append((frame_idx, current_val, ""))
        else:
            debug_data.append((frame_idx, current_val, ""))

        prev_value = current_val

    # 5) Save the debugging CSV
    with open(levels_and_events_csv_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(debug_data)

    print(f"Debugging CSV saved to {levels_and_events_csv_path}")
    print(f"Number of flips detected: {len(flip_frames)}")

    return flip_frames
