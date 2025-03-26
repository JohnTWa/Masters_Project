import csv
import numpy as np
from PIL import Image

def LED_colour_averaging(
    image_path, 
    key_coordinates_csv_path, 
    LED_mask_numpy_path, 
    rgb_averages_csv_path
):
    """
    Similar to 'key_colour_averaging', but uses an LED mask (loaded from a NumPy array)
    to average only those pixels deemed part of the LED region for each bounding box.

    Parameters:
    - image_path (str): Path to the keyboard image (same size as the mask).
    - key_coordinates_csv_path (str): CSV with a 'viewBox' row and subsequent key bounding boxes.
    - LED_mask_numpy_path (str): .npy file containing an RGBA mask array 
                                 (height, width, 4). Non-LED areas are typically (0,0,0,0).
    - rgb_averages_csv_path (str): CSV to which we append one row of R,G,B values 
                                   for each key, in the same format as before.
    """
    # 1) Open the keyboard image
    image = Image.open(image_path).convert('RGB')  # ensure RGB mode
    image_width, image_height = image.size
    image_np = np.array(image)  # shape: (H, W, 3)

    # 2) Load the LED mask array (assumed to be RGBA)
    mask_np = np.load(LED_mask_numpy_path)  # shape: (H, W, 4)
    if mask_np.shape[0] != image_height or mask_np.shape[1] != image_width:
        raise ValueError("Mask dimensions do not match the image dimensions.")

    # 3) Read the key coordinate data (with 'viewBox')
    with open(key_coordinates_csv_path, mode='r', newline='') as infile:
        data = list(csv.reader(infile))

        # Expect first row: ["viewBox", "x y width height"]
        first_row = data[0]
        if first_row[0] == 'viewBox':
            svg_x, svg_y, svg_width, svg_height = map(float, first_row[1].split())
            key_data = data[2:]   # skip second row if it's a header
        else:
            raise ValueError("The CSV file does not contain viewBox information.")

    # 4) Compute scaling from SVG to image
    scale_x = image_width / svg_width
    scale_y = image_height / svg_height

    # We will accumulate the averages for each key and store them in one row
    rgb_values = []

    # 5) For each key bounding box, collect only LED pixels
    for row in key_data:
        # row might be: [key_name, x, y, width, height, ...]
        if len(row) < 5:
            continue
        x, y, w, h = map(float, row[1:5])

        # Scale bounding box to image coordinates
        left   = int(round((x - svg_x) * scale_x))
        top    = int(round((y - svg_y) * scale_y))
        right  = int(round(left + w * scale_x))
        bottom = int(round(top + h * scale_y))

        # Clamp to image boundaries
        left   = max(0, min(image_width, left))
        right  = max(0, min(image_width, right))
        top    = max(0, min(image_height, top))
        bottom = max(0, min(image_height, bottom))

        # 5a) If bounding box is invalid or zero-area, skip
        if left >= right or top >= bottom:
            rgb_values.extend([0, 0, 0])
            continue

        # 5b) Extract the subregion from both image and mask
        sub_img = image_np[top:bottom, left:right, :]    # shape ~ (H', W', 3)
        sub_msk = mask_np[top:bottom, left:right, :]     # shape ~ (H', W', 4)

        # 5c) Find pixels that are 'LED' 
        #     For example, if your mask is pure green for LED => (0,255,0,255).
        #     We'll do a boolean array "led_mask" for those that match that color exactly.
        #     Adjust as needed if you only check alpha or some other condition.
        led_mask = (
            (sub_msk[:,:,0] == 0) &
            (sub_msk[:,:,1] == 255) &
            (sub_msk[:,:,2] == 0) &
            (sub_msk[:,:,3] == 255)
        )

        # Extract only LED pixels from sub_img
        led_pixels = sub_img[led_mask]  # shape (N, 3), where N is # of LED pixels

        if len(led_pixels) == 0:
            # No LED pixels in this box => default to 0,0,0
            avg_r, avg_g, avg_b = 0, 0, 0
        else:
            # Compute average in the LED region
            avg_r = int(np.mean(led_pixels[:, 0]))
            avg_g = int(np.mean(led_pixels[:, 1]))
            avg_b = int(np.mean(led_pixels[:, 2]))

        rgb_values.extend([avg_r, avg_g, avg_b])

    # 6) Write the row of R,G,B values to the CSV file
    with open(rgb_averages_csv_path, mode='a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(rgb_values)

    print(f"Appended LED-only RGB values for this image to {rgb_averages_csv_path}")