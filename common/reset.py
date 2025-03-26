import os
import shutil
import csv

def reset(*paths):
    """
    Deletes the entire contents of any folders given as arguments without deleting the folders themselves,
    and clears the contents of any CSV or TXT files specified.

    Parameters:
    - *paths: Any number of file or folder paths as arguments.
    """
    for path in paths:
        if os.path.isdir(path):  # Check if the path is a directory
            # Delete all contents within the directory
            print(f'Deleting contents of folder at {path}')
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Remove the file
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove the directory and its contents
                except Exception as e:
                    print(f"Failed to delete {item_path}. Reason: {e}")
        elif os.path.isfile(path) and (path.endswith('.csv') or path.endswith('.txt')):  # Check if the path is a CSV or TXT file
            try:
                print(f'Clearing contents of file at {path}')
                open(path, 'w').close()  # Clear the contents of the file
            except Exception as e:
                print(f"Failed to clear contents of {path}. Reason: {e}")
        else:
            print(f"Skipping {path}: Not a recognized folder, CSV, or TXT file.")

# Example usage:
# reset('warped_frames')

def delete_columns(csv_path, first_column, last_column=None):
    """
    Deletes specified columns from a CSV file.

    Parameters:
    - csv_path (str): Path to the CSV file.
    - first_column (int): The first column to delete (1-indexed).
    - last_column (int, optional): The last column to delete (1-indexed). If None, deletes from first_column to the end.

    Returns:
    - None: Modifies the CSV file in place.
    """
    try:
        # Read the CSV file
        with open(csv_path, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        if not rows:
            print("Error: The CSV file is empty.")
            return

        header = rows[0]
        num_columns = len(header)

        # Adjust for 1-indexed column numbers
        first_index = first_column - 1
        last_index = last_column - 1 if last_column else num_columns - 1

        # Validate column indices
        if first_index < 0 or first_index >= num_columns:
            print(f"Error: First column {first_column} is out of range.")
            return
        if last_index < first_index or last_index >= num_columns:
            print(f"Error: Last column {last_column} is out of range.")
            return

        # Delete the specified columns
        new_rows = []
        for row in rows:
            new_row = row[:first_index] + row[last_index + 1:]
            new_rows.append(new_row)

        # Save the modified CSV file
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(new_rows)

        print(f"Columns {first_column} to {last_column if last_column else 'end'} deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
# delete_columns('example.csv', 1, 3)  # Deletes columns 1 to 3 (inclusive)
# delete_columns('example.csv', 4)    # Deletes column 4 to the end

def clear_repeats(signal_csv_path):
    """
    Clears the 'repeat' and 'potential repeat' markers from the 'Change Type' column in the CSV file.

    Parameters:
    - signal_csv_path (str): Path to the input CSV file.

    Returns:
    - None: The updated CSV overwrites the original file.
    """
    try:
        # Read the CSV file
        with open(signal_csv_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Extract the header
            rows = list(reader)
        
        # Validate that 'Change Type' column exists
        if "Change Type" not in header:
            print("Error: 'Change Type' column not found in the CSV.")
            return
        
        change_type_index = header.index("Change Type")
        
        # Replace 'repeat' and 'potential repeat' with an empty string
        for row in rows:
            if row[change_type_index].strip().lower() in ["repeat", "potential repeat"]:
                row[change_type_index] = ""  # Clear the value
        
        # Save the modified rows back to the CSV
        with open(signal_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
        
        print(f"Cleared all 'repeat' and 'potential repeat' markers in {signal_csv_path}.")

    except FileNotFoundError:
        print(f"Error: File not found at {signal_csv_path}.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage:
# clear_repeats("path_to_your_csv.csv")