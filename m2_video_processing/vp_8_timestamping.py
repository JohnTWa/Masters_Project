import cv2
import csv
import os
from datetime import datetime, timedelta

def frame_timestamping(video_path, start_frame, time_at_start_frame, frame_timestamps_csv_path):
    """
    Processes the video file at video_path, and starting from the 0-indexed start_frame,
    produces a CSV file (at frame_timestamps_csv_path) with one row per frame.
    
    Each row is formatted as:
      frame_number, YYYY-MM-DD-HH-MM-SS-mmm
      
    Parameters:
      video_path                : Path to the video file.
      start_frame (int)         : 0-indexed frame number at which the provided timestamp applies.
      time_at_start_frame (str) : Timestamp for the start_frame, in format 'YYYY-MM-DD-HH-MM-SS-mmm'
      frame_timestamps_csv_path : Path to the CSV file to produce.
      
    Example:
      frame_timestamping(video_path, 48, '2025-02-03-17-12-22-000', frame_timestamps_csv_path)
      
    This function writes a CSV where the first row corresponds to frame 48 (the 49th frame if counting from 1)
    and each subsequent row contains the computed timestamp for each frame.
    """
    
    # --- Parse the input timestamp ---
    # The expected format is 'YYYY-MM-DD-HH-MM-SS-mmm' (with mmm being milliseconds).
    # Since datetime.strptime's %f expects 6 digits, we can manually split and build a datetime.
    try:
        parts = time_at_start_frame.split("-")
        if len(parts) != 7:
            raise ValueError("time_at_start_frame must have 7 parts separated by '-'")
        year, month, day, hour, minute, second, msec = parts
        dt_start = datetime(
            int(year), int(month), int(day),
            int(hour), int(minute), int(second),
            int(msec) * 1000  # convert milliseconds to microseconds
        )
    except Exception as e:
        raise ValueError("Error parsing time_at_start_frame. Expected format 'YYYY-MM-DD-HH-MM-SS-mmm'") from e

    # --- Open the video and get FPS ---
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video file: {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise ValueError("Could not determine FPS of video.")
    
    # Determine total frame count (if needed)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Open the CSV file for writing.
    with open(frame_timestamps_csv_path, mode="w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header (optional)
        csv_writer.writerow(["frame_number", "timestamp"])
        
        # Loop over frames from start_frame to the end of the video.
        for frame_number in range(start_frame, total_frames):
            # Compute the elapsed time (in seconds) from start_frame to current frame.
            elapsed_seconds = (frame_number - start_frame) / fps
            # Compute the timestamp for this frame.
            frame_timestamp = dt_start + timedelta(seconds=elapsed_seconds)
            
            # Format the timestamp as 'YYYY-MM-DD-HH-MM-SS-mmm'
            # First, get the standard portion:
            ts_str = frame_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
            # Then append the milliseconds (zero-padded to 3 digits):
            ms_str = f"{int(frame_timestamp.microsecond/1000):03d}"
            formatted_timestamp = f"{ts_str}-{ms_str}"
            
            # Write the row
            csv_writer.writerow([frame_number, formatted_timestamp])
    
    cap.release()
    print(f"Frame timestamps written to {frame_timestamps_csv_path}")