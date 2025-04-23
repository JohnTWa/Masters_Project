import cv2
import numpy as np
import csv

def image_warping(input_image_path, corners_csv_path, warped_image_path, output_width=1000, inverse_gamma=False, gamma=2.2):
# 0) Optional inverse gamma linearization
    image = cv2.imread(input_image_path)
    if image is None:
        raise FileNotFoundError(f"Cannot load image at {input_image_path}")

    if inverse_gamma:
        # Build 256-entry LUT for v_lin = (v/255)^γ * 255
        lut = np.arange(256, dtype=np.float32) / 255.0
        lut = np.power(lut, gamma) * 255.0
        lut = np.clip(lut, 0, 255).astype('uint8')
        # Apply the LUT to all channels
        image = cv2.LUT(image, lut)

    # 1) Read corner points from CSV
    points = []
    with open(corners_csv_path, newline='') as f:
        reader = csv.reader(f)
        headers = next(reader, None)  # skip header if present
        for row in reader:
            x, y = map(float, row[:2])
            points.append((x, y))
    if len(points) != 4:
        raise ValueError(f"Expected 4 corner points, got {len(points)}")

    pts_src = np.array(points, dtype='float32')

    # 2) Compute destination rectangle
    aspect_ratio = 2.64
    width  = output_width
    height = int(width / aspect_ratio)
    pts_dst = np.array([
        [0,       0],
        [width,   0],
        [width, height],
        [0,     height]
    ], dtype='float32')

    # 3) Perspective warp
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(image, M, (width, height))

    # 4) Save result
    cv2.imwrite(warped_image_path, warped)
    print(f"Warped image saved to {warped_image_path}")

# Example usage:

# input_image_path = 'files/i1_picture.jpg'
# corners_csv_path = 'files/s1_corner_coordinates.csv'
# warped_image_path = 'files/i2_warped_image.jpg'

# image_warping(input_image_path, corners_csv_path, warped_image_path)