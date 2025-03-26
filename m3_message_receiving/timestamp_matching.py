import csv
from datetime import datetime, timedelta

def parse_timestamp(ts_str):
    """
    Parses a timestamp string in the format 'YYYY-MM-DD-HH-MM-SS-mmm'
    and returns a datetime object.
    """
    # Split the string into the base part and the milliseconds part.
    try:
        base_str, msec_str = ts_str.rsplit("-", 1)
    except ValueError:
        raise ValueError(f"Timestamp format error: {ts_str}. Expected format 'YYYY-MM-DD-HH-MM-SS-mmm'")
    # Parse the base part using strptime
    dt_base = datetime.strptime(base_str, "%Y-%m-%d-%H-%M-%S")
    # Convert the millisecond part to microseconds (multiply by 1000)
    microsec = int(msec_str) * 1000
    return dt_base.replace(microsecond=microsec)

def frame_colour_matching(set_colours_log, frame_timestamps_csv_path, frame_timestamps_and_colours_csv_path):
    """
    Reads the colour log CSV and the frame timestamps CSV, then produces an output CSV that
    contains, for each frame from the frame timestamps CSV, a matching colour log entry if the
    closest entry is within 0.1 seconds of the frame's timestamp.
    
    The output CSV (frame_timestamps_and_colours_csv_path) has the following columns:
      frame_number, timestamp, R, G, B, matched_log_timestamp
      
    Frames that do not have a corresponding colour log entry within 0.1 seconds are omitted from
    the output, and a warning is printed with the frame number and its timestamp.
    
    At the end, summary statistics are printed:
      - Total number of frames.
      - Total number of colour log entries.
      - Number of frames with corresponding log entries.
      - Number of frames without corresponding log entries.
      - Number of log entries without corresponding frames.
    """
    
    # --- Read the colour log CSV ---
    colour_logs = []  # list of dictionaries; expected keys: timestamp, R, G, B, (and optionally segment)
    with open(set_colours_log, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = parse_timestamp(row["timestamp"])
            except Exception as e:
                raise ValueError(f"Error parsing timestamp in colour log: {row['timestamp']}") from e
            colour_logs.append({
                "timestamp": ts,
                "r": int(row["R"]),
                "g": int(row["G"]),
                "b": int(row["B"]),
                "segment": row.get("segment", "")
            })
    
    # --- Read the frame timestamps CSV ---
    frames = []  # list of dictionaries; expected keys: frame_number, timestamp
    with open(frame_timestamps_csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = parse_timestamp(row["timestamp"])
            except Exception as e:
                raise ValueError(f"Error parsing timestamp in frame CSV: {row['timestamp']}") from e
            frames.append({
                "frame_number": int(row["frame_number"]),
                "timestamp": ts
            })
    
    # --- Match each frame to the closest colour log entry ---
    matched_logs_indices = set()
    frames_with_match = 0
    frames_without_match = 0
    output_entries = []  # to store rows for output CSV
    
    for frame in frames:
        frame_ts = frame["timestamp"]
        best_diff = None
        best_log_index = None
        best_log = None
        # Find the colour log entry with minimal absolute time difference
        for i, log_entry in enumerate(colour_logs):
            diff = abs((log_entry["timestamp"] - frame_ts).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_log_index = i
                best_log = log_entry
        # If the best match is within 0.1 seconds, include the frame in the output.
        if best_diff is not None and best_diff <= 0.1:
            # Format timestamps back to the desired format: YYYY-MM-DD-HH-MM-SS-mmm
            frame_ts_str = frame_ts.strftime("%Y-%m-%d-%H-%M-%S") + "-" + f"{int(frame_ts.microsecond/1000):03d}"
            log_ts_str = best_log["timestamp"].strftime("%Y-%m-%d-%H-%M-%S") + "-" + f"{int(best_log['timestamp'].microsecond/1000):03d}"
            output_entries.append({
                "frame_number": frame["frame_number"],
                "timestamp": frame_ts_str,
                "R": best_log["r"],
                "G": best_log["g"],
                "B": best_log["b"],
                "matched_log_timestamp": log_ts_str
            })
            frames_with_match += 1
            matched_logs_indices.add(best_log_index)
        else:
            frames_without_match += 1
            frame_ts_str = frame_ts.strftime("%Y-%m-%d-%H-%M-%S") + "-" + f"{int(frame_ts.microsecond/1000):03d}"
            print(f"Warning: Frame {frame['frame_number']} with timestamp {frame_ts_str} is more than 0.1 seconds away from any log entry.")
    
    # --- Write the output CSV ---
    fieldnames = ["frame_number", "timestamp", "R", "G", "B", "matched_log_timestamp"]
    with open(frame_timestamps_and_colours_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in output_entries:
            writer.writerow(entry)
    
    # --- Summary statistics ---
    num_frames = len(frames)
    num_logs = len(colour_logs)
    num_matched_frames = frames_with_match
    num_unmatched_frames = frames_without_match
    num_unmatched_logs = num_logs - len(matched_logs_indices)
    
    print("Summary:")
    print(f"Total frames: {num_frames}")
    print(f"Total colour log entries: {num_logs}")
    print(f"Frames with corresponding log entries: {num_matched_frames}")
    print(f"Frames without corresponding log entries: {num_unmatched_frames}")
    print(f"Log entries without corresponding frames: {num_unmatched_logs}")

# Example usage:
frame_colour_matching("files/l1_colour_sent.log", "files/s5_frame_timestamps.csv", "files/s6_frame_timestamps_and_colours.csv")