import cv2
import numpy as np
import csv

def image_warping(input_image_path, corners_csv_path, warped_image_path, output_width=1000):
    # Fixed aspect ratio
    aspect_ratio = 2.64

    # Load the image
    image = cv2.imread(input_image_path)

    # Load points from the CSV file
    points = []
    with open(corners_csv_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            x, y = map(float, row)
            points.append((x, y))

    # Points from CSV file
    pts_src = np.array(points, dtype='float32')

    # Define the desired destination points (top-left, top-right, bottom-right, bottom-left)
    height = int(output_width / aspect_ratio)
    pts_dst = np.array([[0, 0], [output_width, 0], [output_width, height], [0, height]], dtype='float32')

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # Apply the perspective transformation to the image
    warped = cv2.warpPerspective(image, matrix, (output_width, height))

    # Save the transformed image
    cv2.imwrite(warped_image_path, warped)
    print(f"Warped image saved to {warped_image_path}")

# Example usage:

# input_image_path = 'files/i1_picture.jpg'
# corners_csv_path = 'files/s1_corner_coordinates.csv'
# warped_image_path = 'files/i2_warped_image.jpg'

# image_warping(input_image_path, corners_csv_path, warped_image_path)