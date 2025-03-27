from _SETUP_ import set_directory
set_directory()

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# Local Functions
from common.image_displaying import display_image

def image_to_pbm(input_path, output_path, resolution):
    """
    Converts an image to a PBM (Portable Bitmap) file with the specified square resolution.
    If the image is not square, it is centrally cropped to form a square before resizing.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path to save the output PBM file.
        resolution (int): Desired width and height (in pixels) for the output square image.
    """
    # Open the image and convert to grayscale.
    img = Image.open(input_path).convert('L')
    
    # Crop the image to a square by using the smallest dimension.
    width, height = img.size
    if width != height:
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))
    
    # Resize the image to the desired resolution.
    img = img.resize((resolution, resolution), Image.Resampling.LANCZOS)
    
    # Convert the image to binary (1-bit) using the default threshold.
    img = img.convert('1')
    
    # Save the image in PBM format.
    img.save(output_path)

def display_pgm_or_pbm(file_path):
    # Open the image using Pillow
    image = Image.open(file_path)
    
    # Convert image to grayscale (mode 'L') to standardize the display.
    image = image.convert("L")
    
    # Convert the Pillow image to a NumPy array for display.
    image_array = np.array(image)
    
    # Display the image using Matplotlib.
    plt.imshow(image_array, cmap='gray', vmin=0, vmax=255)
    plt.title(f"Image: {file_path}")
    plt.axis('off')
    plt.show()

def convert_p4_to_p1(input_file_path, output_file_path):
    """
    Converts a binary PBM (P4) file into an ASCII PBM (P1) file.
    
    Args:
        input_file_path (str): Path to the input binary PBM (P4) file.
        output_file_path (str): Path to write the output ASCII PBM (P1) file.
    
    Raises:
        ValueError: If the input file is not in P4 format.
    """
    # Open the input file in binary mode.
    with open(input_file_path, 'rb') as infile:
        # Read the magic number and verify it's P4.
        magic_number = infile.readline().strip()
        if magic_number != b'P4':
            raise ValueError("Input file is not in binary PBM (P4) format.")
        
        # Read header lines (skip comments).
        header_data = []
        while len(header_data) < 2:
            line = infile.readline().strip()
            if line.startswith(b'#'):
                continue
            header_data.extend(line.split())
        width = int(header_data[0])
        height = int(header_data[1])
        
        # Calculate the number of bytes per row. Each row is padded to a full byte.
        row_bytes = math.ceil(width / 8)
        
        # Initialize a list to hold rows of pixel values (as strings "0" or "1")
        ascii_rows = []
        for row in range(height):
            # Read one row of binary data.
            row_data = infile.read(row_bytes)
            row_pixels = []
            for byte in row_data:
                # Process each bit in the byte.
                for bit in range(7, -1, -1):
                    # Extract the bit.
                    pixel = (byte >> bit) & 1
                    row_pixels.append(str(pixel))
                    # Stop if we've reached the row's width.
                    if len(row_pixels) == width:
                        break
            ascii_rows.append(" ".join(row_pixels))
    
    # Write the ASCII PBM (P1) file.
    with open(output_file_path, 'w', encoding='ascii') as outfile:
        outfile.write("P1\n")
        outfile.write(f"{width} {height}\n")
        for row in ascii_rows:
            outfile.write(row + "\n")

def split_pbm_rows(file_path):
    """
    Reads an ASCII PBM (P1) file and splits its pixel data into rows.
    
    Each row is returned as a list of integers (0s and 1s). The file must
    conform to the ASCII PBM format.

    Args:
        file_path (str): The path to the PBM file.
    
    Returns:
        List[List[int]]: A list of rows, where each row is a list of 0s and 1s.
    
    Raises:
        ValueError: If the file is not in the expected ASCII PBM (P1) format.
        FileNotFoundError: If the specified file does not exist.
    """
    try:
        with open(file_path, 'r', encoding='ascii', errors='replace') as file:
            # Read and validate the magic number.
            magic_number = file.readline().strip()
            if magic_number != "P1":
                raise ValueError("Unsupported PBM format. This function only supports ASCII PBM (P1).")
            
            # Read header lines: skip comments (lines starting with '#').
            header_data = []
            while len(header_data) < 2:
                line = file.readline().strip()
                if line.startswith("#"):
                    continue
                header_data.extend(line.split())
            
            # Parse image dimensions: width and height.
            width, height = int(header_data[0]), int(header_data[1])
            
            # Read the pixel data.
            pixels = []
            # Continue reading until we have width * height values.
            while len(pixels) < width * height:
                line = file.readline().strip()
                if line.startswith("#") or not line:
                    continue  # Skip any comment or empty lines.
                # Extend pixel list with values from this line.
                pixels.extend([int(value) for value in line.split()])
            
            # Convert the flat list of pixels into a list of rows.
            rows = [pixels[i * width:(i + 1) * width] for i in range(height)]
            return rows
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} does not exist.")
    
def split_row_into_8bit_chunks(row):
    return [row[i:i+8] for i in range(0, len(row), 8)]

def recombine_8bit_chunks(chunks):
    row = []
    for chunk in chunks:
        row.extend(chunk)
    return row

def write_p1_from_rows(rows, output_file_path):
    """
    Writes a P1 (ASCII PBM) image file using a list of rows.
    
    Each row is expected to be a list of integers (0s and 1s). The function
    writes the standard P1 header followed by the pixel data, with pixels in each row
    separated by spaces.
    
    Args:
        rows (List[List[int]]): A list of rows, where each row is a list of 0s and 1s.
        output_file_path (str): The path where the P1 file will be saved.
    
    Raises:
        ValueError: If rows is empty or if rows have inconsistent widths.
    """
    if not rows or not rows[0]:
        raise ValueError("Rows list is empty or improperly formatted.")
    
    height = len(rows)
    width = len(rows[0])
    
    # Check that all rows have the same width.
    for row in rows:
        if len(row) != width:
            raise ValueError("All rows must have the same number of pixels.")
    
    with open(output_file_path, "w", encoding="ascii") as f:
        # Write the header
        f.write("P1\n")
        f.write(f"{width} {height}\n")
        # Write each row as a space-separated string of 0s and 1s.
        for row in rows:
            line = " ".join(str(bit) for bit in row)
            f.write(line + "\n")

if __name__ == '__main__':
    
    # Display the PBM image
    image_path = 'files\images\dog.jpg'
    p4_image_path = f'{os.path.splitext(image_path)[0]}_P4.pbm'
    p1_image_path = f'{os.path.splitext(image_path)[0]}_P1.pbm'

    # Convert the image to a PBM file
    display_pgm_or_pbm(image_path)
    image_to_pbm(image_path, p4_image_path, 256)
    convert_p4_to_p1(p4_image_path, p1_image_path)
    display_pgm_or_pbm(p1_image_path)

    rows = split_pbm_rows(p1_image_path)
    rows_of_chunks = []
    for row in rows:
        chunks = (split_row_into_8bit_chunks(row))
        rows_of_chunks.append(chunks)

    # COMMUNICATION GOES HERE

    recombined_rows = []
    for row in rows_of_chunks:
        recombined_rows.append(recombine_8bit_chunks(row))
    
    write_p1_from_rows(recombined_rows, "files/images/small_sample_ascii_recombined.pbm")
    display_pgm_or_pbm("files/images/small_sample_ascii_recombined.pbm")