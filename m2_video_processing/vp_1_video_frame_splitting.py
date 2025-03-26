import cv2
import os

def video_frame_splitting(video_path, frames_path):

    os.makedirs(frames_path, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    else:
        print(f'Splitting {video_path} into {frames_path}')

    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(os.path.join(frames_path, f'frame_{frame_number}.png'), frame)
        frame_number += 1

    cap.release()
    print(f"Frames saved in '{frames_path}'.")

# Example usage:

# video_path = 'files/m1_video.mp4'
# input_image_path = 'files/i1_picture.jpg'

#video_frame_splitting(video_path, frames_path)