from _SETUP_ import set_directory
set_directory()

import csv
import os
import numpy as np
from PIL import Image

from common.image_displaying import display_image, produce_overlaid_image

def LED_identification(
    image_path,
    key_coordinates_csv_path,
    LED_mask_image_path,
    LED_mask_numpy_path,
    ycbcr_thresholds=None
):
    """
    Identifies 'red' LED regions in each key boundary of a keyboard image, using YCbCr color space.
    Saves a backgroundless green mask (as a PNG) for visualization, and a corresponding NumPy
    array for programmatic use.

    Parameters:
    - image_path (str): Path to the input image of the keyboard.
    - key_coordinates_csv_path (str): CSV containing a 'viewBox' row and subsequent key boundary rows:
          [ 0 ]: 'viewBox'
          [ 1 ]: e.g. "0 0 500 200"  (x, y, width, height in SVG units)
          [2+]: rows containing at least (key_name, x, y, width, height, ...)
    - LED_mask_image_path (str): Where to save the mask as a PNG (transparent outside the LED).
    - LED_mask_numpy_path (str): Where to save the mask as a NumPy array (.npy).
    - ycbcr_thresholds (dict or None): thresholds for detecting red in YCbCr, e.g.
          {
            "Cr_min": 150, "Cr_max": 200,
            "Cb_min":  40, "Cb_max": 140
          }
      If None, default thresholds are used.
    """

    if ycbcr_thresholds is None:
        # Example defaults. Adjust as needed for your particular LEDs/lighting.
        ycbcr_thresholds = {
            "Cr_min": 150, "Cr_max": 255,  # typical 'red' => higher Cr
            "Cb_min":  0,   "Cb_max": 130  # typical 'red' => lower Cb
        }

    def is_red_pixel(Y, Cb, Cr):
        """
        Returns True if the YCbCr pixel is "red" by the current threshold logic.
        Modify as needed for your environment.
        """
        return (ycbcr_thresholds["Cr_min"] <= Cr <= ycbcr_thresholds["Cr_max"] and
                ycbcr_thresholds["Cb_min"] <= Cb <= ycbcr_thresholds["Cb_max"])
    
    # 1) Open the image, convert to YCbCr for easier red detection
    image = Image.open(image_path).convert('YCbCr')
    image_width, image_height = image.size

    # 2) Parse the keyboard vector CSV
    with open(key_coordinates_csv_path, mode='r', newline='') as infile:
        reader = list(csv.reader(infile))
        # Expect first row: ['viewBox', '0 0 500 200'] or similar
        if len(reader) < 3 or reader[0][0] != 'viewBox':
            raise ValueError("key_coordinates_csv_path CSV must have a 'viewBox' in the first row.")

        # Parse viewBox
        svg_x, svg_y, svg_w, svg_h = map(float, reader[0][1].split())

        # The next row might be a header (like column names). 
        # Then actual key data rows follow (we'll skip the second row for safety):
        key_data = reader[2:]

    # 3) Compute scaling factors from SVG units to image pixels
    scale_x = image_width / svg_w
    scale_y = image_height / svg_h

    # 4) Create a new RGBA image for the mask, starting fully transparent
    mask_image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    mask_pixels = mask_image.load()

    # Also get pixel access for the YCbCr image
    source_pixels = image.load()

    # 5) For each key boundary, iterate over its region and detect red
    for row in key_data:
        # row might look like: [keyname, x, y, width, height, ...]
        # ensure we have at least 5 columns
        if len(row) < 5:
            continue
        x, y, w, h = map(float, row[1:5])  # skip the key name in row[0]

        # Convert to image-space coordinates
        # (x - svg_x) moves the offset from the left of the viewBox
        left   = int(round((x - svg_x) * scale_x))
        top    = int(round((y - svg_y) * scale_y))
        right  = int(round(left + w * scale_x))
        bottom = int(round(top + h * scale_y))

        # Clamp to image bounds (just in case)
        left   = max(0, min(image_width, left))
        right  = max(0, min(image_width, right))
        top    = max(0, min(image_height, top))
        bottom = max(0, min(image_height, bottom))

        # Now check each pixel in this region
        for px in range(left, right):
            for py in range(top, bottom):
                Y, Cb, Cr = source_pixels[px, py]
                if is_red_pixel(Y, Cb, Cr):
                    # Mark as green with full alpha
                    mask_pixels[px, py] = (0, 255, 0, 255)

    # 6) Save mask as a PNG
    mask_image.save(LED_mask_image_path, "PNG")
    print(f"Saved LED mask visualization to: {LED_mask_image_path}")

    # 7) Also save mask as a NumPy array
    #    We'll convert the RGBA image to a NumPy array of shape (height, width, 4)
    mask_array = np.array(mask_image)
    np.save(LED_mask_numpy_path, mask_array)
    print(f"Saved LED mask NumPy array to: {LED_mask_numpy_path}")

# Example usage:
# LED_identification(
#     image_path="files/warped_frames//warped_frame_0.png",
#     key_coordinates_csv_path="files/s2_key_coordinates.csv",
#     LED_mask_image_path="files/i5_LED_mask.png",
#     LED_mask_numpy_path="files/a1_LED_mask.npy",
#     ycbcr_thresholds={
#         "Cr_min": 150, "Cr_max": 255,
#         "Cb_min":  0,   "Cb_max": 130
#     }
# )

# produce_overlaid_image(
#     warped_vector_path=None,
#     input_image_path="files/i2_warped_image.png",
#     overlay_image_path="files/i5_LED_mask.png",
#     overlaid_image_path="files/i6_LED_overlay.png"
# )

# display_image("files/i6_LED_overlay.png")