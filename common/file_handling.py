import csv
import string

def write_to_csv_new_row(csv_path, *args):
    """
    Writes any provided arguments to a CSV file, each argument in a new column, and adds a new row for each call.

    Parameters:
    - csv_path (str): Path to the output CSV file.
    - *args: Arguments to be written to the CSV file.
    """
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(args)

def write_to_csv_new_column(csv_path, row_number, *args):
    """
    Writes the provided arguments to a specific row in a CSV file, adding them as new columns 
    following existing data in that row. Does not overwrite existing data.

    Parameters:
    - csv_path (str): Path to the CSV file.
    - row_number (int): The 1-based row number to write to.
    - *args: Data to be written to new columns in the specified row.
    """
    try:
        # Read the existing CSV file
        with open(csv_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Adjust for 1-based row numbering
        target_index = row_number - 1

        # Ensure the target row exists
        while len(rows) <= target_index:
            rows.append([])

        # Append new data to the target row
        rows[target_index].extend(args)

        # Write back the modified data
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}. Creating a new file.")
        # Create a new file with the specified row and write data
        rows = []
        for _ in range(row_number - 1):
            rows.append([])  # Create empty rows
        rows.append(list(args))  # Add data to the target row
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    except Exception as e:
        print(f"Unexpected error: {e}")

def append_to_txt(txt_path, row_number, *args):
    """
    Appends the provided single-character arguments as a string to a specific row in a text file.
    If the row does not exist, it creates empty rows until the target row is reached.

    Only single printable ASCII characters are accepted; multi-character strings are ignored.

    Parameters:
    - txt_path (str): Path to the text file.
    - row_number (int): The 1-based row number to append the data to.
    - *args: Data to be concatenated and appended to the specified row.
    """
    try:
        # Create a filter for printable single ASCII characters
        allowed_chars = set(string.ascii_letters + string.digits + string.punctuation + ' ')

        # Filter the arguments to include only single allowed characters
        args_str = ''.join(arg for arg in args if len(arg) == 1 and arg in allowed_chars)

        # Read the existing text file
        try:
            with open(txt_path, mode='r', encoding='ascii') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"File not found at {txt_path}. Creating a new file.")
            lines = []

        # Ensure the target row exists
        while len(lines) < row_number:
            lines.append("\n")

        # Append the filtered string to the specified row
        lines[row_number - 1] = lines[row_number - 1].rstrip("\n") + args_str + "\n"

        # Write back to the text file
        with open(txt_path, mode='w', encoding='ascii') as file:
            file.writelines(lines)

    except Exception as e:
        print(f"Unexpected error: {e}")

def csv_to_tuple(file_path):
    numbers = []
    
    # Open and read the CSV file
    with open(file_path, mode='r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            # Each row may contain multiple columns, convert all to integers
            numbers.extend(int(num) for num in row if num.isdigit())
    
    # Return numbers as a tuple
    return tuple(numbers)

def csv_to_list(file_path):
    numbers = []
    
    # Open and read the CSV file
    with open(file_path, mode='r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            # Each row may contain multiple columns, convert all to integers
            numbers.extend(int(num) for num in row if num.isdigit())
    
    # Return numbers as a list
    return list(numbers)

def adjust_for_Corsair_logo(key_IDs):
    for i in range(len(key_IDs)-1):
        if key_IDs[i] == 196609 and key_IDs[i+1] == 196610:
            key_IDs[i] = 0
            key_IDs.remove(196610)
    return key_IDs