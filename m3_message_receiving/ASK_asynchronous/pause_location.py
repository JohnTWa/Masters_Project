import csv

def determine_pause_bounds(signal_csv_path, pause_rows, mark=False):
    """
    Determines pause bounds in a signal CSV file and optionally marks them in a new column.
    
    Parameters:
    - signal_csv_path (str): Path to the CSV file containing signal data.
    - pause_rows (int): The number of rows without a flip to qualify as a pause.
    - mark (bool): Whether to mark the pauses in the CSV file (default is False).
    
    Returns:
    - tuple: A tuple of pause bounds in the form ((pause1_start, pause1_end), (pause2_start, pause2_end), ...).
    """
    rows = []
    header = []
    pause_bounds = []

    try:
        # Read the CSV and validate headers
        with open(signal_csv_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = list(reader)

        # Validate required headers
        if header.count("Value") > 1 or header.count("Change Type") > 1:
            raise ValueError("Error: Required column headers are repeated.")
        if "Value" not in header or "Change Type" not in header:
            raise ValueError("Error: Required column headers 'Value' and 'Change Type' are missing.")

        if "Pause Bounds" in header and mark:
            print("Warning: 'Pause Bounds' column already exists. Proceeding without marking pauses.")
            mark = False

        # Identify column indices
        value_index = header.index("Value")
        change_type_index = header.index("Change Type")
        pause_bounds_index = None

        if mark and "Pause Bounds" not in header:
            header.append("Pause Bounds")
            pause_bounds_index = len(header) - 1

        # Process rows to determine pauses
        last_flip_row = None
        current_pause_start = 0  # Start tracking pauses from the beginning

        for i, row in enumerate(rows):
            # Ensure the row has enough columns
            if len(row) < len(header):
                row.extend([""] * (len(header) - len(row)))

            flip_state = row[change_type_index].strip().lower()

            if flip_state in ["up", "down"]:
                # Handle any ongoing pause before this flip
                if current_pause_start is not None:
                    pause_end = i
                    if pause_end - current_pause_start >= pause_rows:
                        # Add 2 to account for 1-based row numbering and the header row
                        pause_bounds.append((current_pause_start + 2, pause_end + 1))
                        if mark:
                            rows[current_pause_start][pause_bounds_index] = f"pause{len(pause_bounds)}_start"
                            rows[pause_end][pause_bounds_index] = f"pause{len(pause_bounds)}_end"
                    current_pause_start = None

                last_flip_row = i

            elif last_flip_row is not None and current_pause_start is None:
                # Start a new pause
                if i - last_flip_row > 1:  # Ensure it's not a consecutive row
                    current_pause_start = last_flip_row + 1

        # Handle trailing pause at the end of the file
        if current_pause_start is not None and len(rows) - current_pause_start >= pause_rows:
            pause_bounds.append((current_pause_start + 2, len(rows) + 1))
            if mark:
                rows[current_pause_start][pause_bounds_index] = f"pause{len(pause_bounds)}_start"
                rows[-1][pause_bounds_index] = f"pause{len(pause_bounds)}_end"

        # Handle initial pause before the first flip
        if last_flip_row is None and len(rows) >= pause_rows:
            pause_bounds.append((2, pause_rows + 1))
            if mark:
                rows[0][pause_bounds_index] = f"pause{len(pause_bounds)}_start"
                rows[pause_rows - 1][pause_bounds_index] = f"pause{len(pause_bounds)}_end"

        # Print results
        if not pause_bounds:
            print("Warning: No pauses found in the specified CSV file.")
        else:
            print(f"Detected {len(pause_bounds)} pause(s).")

        # Save the modified CSV if marking is enabled
        if mark:
            with open(signal_csv_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(rows)
            print(f"Pauses marked in the CSV file at {signal_csv_path}")

    except ValueError as ve:
        print(ve)
        return ()
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return ()

    return tuple(pause_bounds)

# Example usage:
# pause_bounds = determine_pause_bounds("signal.csv", pause_rows=50, mark=True)
# print(pause_bounds)