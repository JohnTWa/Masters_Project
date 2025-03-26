from _SETUP_ import set_directory
set_directory()

import os
import pandas as pd

def normalise_rgb(rgb_averages_csv, normalised_rgb_averages_csv):
    """
    Reads an RGB averages CSV (assumed to have no header) and normalises each column
    so that the minimum value becomes 0 and the maximum value becomes 255. All values
    are converted to integers. The resulting CSV is saved to normalised_rgb_averages_csv.
    """
    df = pd.read_csv(rgb_averages_csv, header=None)
    
    for col in df.columns:
        col_min = df[col].min()
        col_max = df[col].max()
        df[col] = ((df[col] - col_min) / (col_max - col_min) * 255).round().astype(int)
    
    df.to_csv(normalised_rgb_averages_csv, header=False, index=False)

def t_t_split(frame_timestamps_and_colours_csv_path, train_proportion=0.7):
    """
    Splits the frames (and their target RGB values) from the CSV into training and testing sets.
    """
    # Check that the file exists.
    if not os.path.exists(frame_timestamps_and_colours_csv_path):
        raise FileNotFoundError(f"Target CSV file not found: {frame_timestamps_and_colours_csv_path}")
    
    # Read the CSV file.
    df = pd.read_csv(frame_timestamps_and_colours_csv_path)
    if df.empty:
        raise ValueError(f"Target CSV file is empty: {frame_timestamps_and_colours_csv_path}")
    
    # Check that required columns are present.
    required_columns = {"frame_number", "R", "G", "B"}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"Target CSV file must contain the columns {required_columns}. Found columns: {list(df.columns)}")
    
    # Sort by frame_number to ensure a contiguous split.
    df = df.sort_values("frame_number").reset_index(drop=True)
    
    total_frames = len(df)
    n_train = int(total_frames * train_proportion)
    
    # Create contiguous splits.
    train_df = df.iloc[:n_train].copy()
    test_df = df.iloc[n_train:].copy()
    
    # Extract frame numbers.
    train_frames = train_df["frame_number"].tolist()
    test_frames = test_df["frame_number"].tolist()
    
    # Build target DataFrames with column name "frame_n" instead of "frame_number"
    train_targets = train_df[["frame_number", "R", "G", "B"]].rename(
        columns={"frame_number": "frame_n"}
    ).reset_index(drop=True)
    test_targets = test_df[["frame_number", "R", "G", "B"]].rename(
        columns={"frame_number": "frame_n"}
    ).reset_index(drop=True)
    
    return train_frames, test_frames, train_targets, test_targets

def load_rgb_features(rgb_csv_path:str, train_frames:list, test_frames:list, key:int):
    '''
    Loads the RGB features from the CSV file for the training and testing frames into a Pandas dataframe.
    '''
    data = pd.read_csv(rgb_csv_path, header=None)

    def extract_features(frame_numbers, data):

        # Index csv rows by frame number
        selected = data.iloc[frame_numbers].copy()
        
        # Extract RGB values for frame numbers at key
        R = selected.iloc[:, (key-1)*3]
        G = selected.iloc[:, (key-1)*3 + 1]
        B = selected.iloc[:, (key-1)*3 + 2]

        # Load to dictionary then to dataframe
        features = {
            'frame_n': frame_numbers,
            'R': R,
            'G': G,
            'B': B}
        features_table = pd.DataFrame(features)

        return features_table
    
    train_features = extract_features(train_frames, data)
    test_features = extract_features(test_frames, data)
    
    return train_features, test_features

# Example usage

# train_frames, test_frames, train_target, test_target = t_t_split("files/s6_frame_timestamps_and_colours.csv", train_proportion=0.7)
# train_features, test_features = load_rgb_features("files/s3_rgb_averages.csv", train_frames, test_frames, key=1)