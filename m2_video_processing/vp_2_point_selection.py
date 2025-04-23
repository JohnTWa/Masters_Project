import cv2
import csv

def point_selection(input_image_path, corners_csv_path,
                    max_width=1024, max_height=768):
    """
    Let the user pick four corner points on an image, saving them in original
    pixel coordinates. The display window is capped to max_width×max_height.
    """
    # 1) Load full‑resolution image
    orig = cv2.imread(input_image_path)
    if orig is None:
        raise FileNotFoundError(f"Could not load image at {input_image_path}")
    h0, w0 = orig.shape[:2]

    # 2) Compute display scale (<=1.0)
    scale = min(max_width / w0, max_height / h0, 1.0)
    disp_w, disp_h = int(w0 * scale), int(h0 * scale)

    # 3) Create a scaled copy for display
    disp = cv2.resize(orig, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

    # 4) Prepare window
    cv2.namedWindow('Select Corners', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Select Corners', disp_w, disp_h)

    points = []

    def select_points(event, x, y, flags, param):
        # x,y are on the *display* image, so map back to original coords
        if event == cv2.EVENT_LBUTTONDOWN:
            ox = int(x / scale)
            oy = int(y / scale)
            points.append((ox, oy))
            # mark on the display copy
            cv2.circle(disp, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow('Select Corners', disp)
            if len(points) == 4:
                cv2.destroyAllWindows()

    cv2.setMouseCallback('Select Corners', select_points)

    # 5) Show and wait for exactly 4 clicks
    while len(points) < 4:
        cv2.imshow('Select Corners', disp)
        if cv2.waitKey(10) == 27:  # allow ESC to abort
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("Point selection aborted by user")

    # 6) Save to CSV in original pixel coordinates
    with open(corners_csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y'])
        writer.writerows(points)

    print(f"Selected points saved to {corners_csv_path}")

# Example usage:

# input_input_image_path = 'files/i1_picture.jpg'
# corners_csv_path = 'files/s1_corner_coordinates.csv'

# point_selection(input_input_image_path, corners_csv_path)