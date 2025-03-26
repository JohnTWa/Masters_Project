import cv2
import csv

def point_selection(input_image_path, corners_csv_path):
    # Load the image
    image = cv2.imread(input_image_path)
    
    # Create a window to display the image
    cv2.namedWindow('Select Corners')
    points = []

    # Callback function for mouse click events to capture points
    def select_points(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Select Corners", image)
            if len(points) == 4:
                cv2.destroyAllWindows()

    # Set mouse callback function for window
    cv2.setMouseCallback('Select Corners', select_points)

    # Display the image and wait for user to select 4 points
    while len(points) < 4:
        cv2.imshow('Select Corners', image)
        cv2.waitKey(1)

    # Save the selected points to a CSV file
    with open(corners_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x', 'y'])
        writer.writerows(points)
    print(f"Selected points saved to {corners_csv_path}")

# Example usage:

# input_input_image_path = 'files/i1_picture.jpg'
# corners_csv_path = 'files/s1_corner_coordinates.csv'

# point_selection(input_input_image_path, corners_csv_path)