import numpy as np
import pandas as pd
from _SETUP_ import set_directory
set_directory()
from common.reset import reset
from m4_demodulation_and_decoding.edge_detection import detect_edges_with_orig_index
from sklearn.metrics import r2_score


def load_target_data(path, delimiter=','):
    # Load CSV where each row is R,G,B,R,G,B,...
    data = np.loadtxt(path, delimiter=delimiter)
    # Ensure 2D even if there's only one row
    if data.ndim == 1:
        data = data[np.newaxis, :]
    rows, cols = data.shape
    if cols % 3 != 0:
        raise ValueError(f"Expected columns to be a multiple of 3, got {cols}")
    # Reshape into (n_samples, 3)
    samples = data.reshape(rows * (cols // 3), 3)
    return samples

def load_raw_data(path, row_indices, CLK_key_n=0, delimiter=','):
    """
    Load a CSV where each row is [R, G, B, R, G, B, …],
    select only the specified rows, drop one triple-group of columns,
    and return the rest as a flat list of RGB triples.

    Parameters
    ----------
    path : str
        Path to the CSV file.
    row_indices : Sequence[int]
        Zero‑based indices of rows to extract.
    CLK_key_n : int, optional
        Which 3‑column group to drop (0 drops cols 0–2, 1 drops cols 3–5, etc.).
        Default is 0.
    delimiter : str, optional
        Field delimiter in the CSV (default is ',').

    Returns
    -------
    samples : ndarray, shape (n_samples, 3)
        A 2D array of RGB triples, where
        n_samples = len(row_indices) * ((n_cols_per_row - 3) // 3).
    """
    # 1) Load entire CSV into a 2D NumPy array
    data = np.loadtxt(path, delimiter=delimiter)
    if data.ndim == 1:
        data = data[np.newaxis, :]

    # 2) Select only the rows we care about
    selected = data[row_indices, :]

    # 3) Validate that each row has a multiple of 3 columns
    n_rows, n_flat = selected.shape
    if n_flat % 3 != 0:
        raise ValueError(f"CSV columns ({n_flat}) not a multiple of 3.")

    # 4) Determine which columns to drop
    n_groups = n_flat // 3
    if not (0 <= CLK_key_n < n_groups):
        raise ValueError(f"CLK_key_n={CLK_key_n} out of range; "
                         f"must be in [0, {n_groups-1}]")
    start = CLK_key_n * 3
    end   = start + 3

    # 5) Drop the specified 3‑column group
    #    (axis=1 means drop columns)
    trimmed = np.delete(selected, np.s_[start:end], axis=1)

    # 6) Reshape into a flat list of RGB triples
    new_flat = n_flat - 3
    samples = trimmed.reshape(n_rows * (new_flat // 3), 3)

    return samples

def train_test_split(raw, target, test_size=0.2, random_state=19450716112921):
    """
    Split raw and target arrays into train/test subsets.
    """
    raw = np.asarray(raw)
    target = np.asarray(target)
    if raw.shape[0] != target.shape[0]:
        raise ValueError("raw and target must have the same number of samples")
    n = raw.shape[0]

    # Determine number of test samples
    if isinstance(test_size, float):
        n_test = int(n * test_size)
    elif isinstance(test_size, int):
        n_test = test_size
    else:
        raise ValueError("test_size must be float or int")
    if not (0 <= n_test <= n):
        raise ValueError("test_size out of range")

    # Shuffle indices reproducibly
    rng = np.random.default_rng(random_state)
    idx = np.arange(n)
    rng.shuffle(idx)

    test_idx = idx[:n_test]
    train_idx = idx[n_test:]

    return (
        raw[train_idx],  # raw train
        raw[test_idx],   # raw test
        target[train_idx],  # target train
        target[test_idx],   # target test
    )

def compute_color_correction_matrix(raw, target):
    # Solve raw @ X = target in the least-squares sense, then transpose
    X, *_ = np.linalg.lstsq(raw, target, rcond=None)
    return X.T

def main(raw_csv, CLK_csv, target_csv, ccm_npy, metrics_csv, data_npz,
         test_size=0.2, random_state=19450716112921):
    # 1) Find CLK edges and sample accordingly
    reset(CLK_csv)
    CLK = detect_edges_with_orig_index(raw_csv, 0, CLK_csv, threshold_fraction=0.2)

    # 2) load
    raw_samples    = load_raw_data(raw_csv, CLK)
    target_samples = load_target_data(target_csv)

    # 3) check & align lengths
    n_raw = raw_samples.shape[0]
    n_tgt = target_samples.shape[0]
    if n_raw != n_tgt:
        n_keep = min(n_raw, n_tgt)
        print(f"WARNING: sample-count mismatch (raw={n_raw}, target={n_tgt}); "
              f"truncating both to {n_keep} samples")
        raw_samples    = raw_samples[-n_keep:]
        target_samples = target_samples[-n_keep:]
        print(f"First raw sample: {raw_samples[0]} and target: {target_samples[0]}")

    # 4) train/test split
    raw_train, raw_test, tgt_train, tgt_test = train_test_split(
        raw_samples, target_samples,
        test_size=test_size, random_state=random_state
    )

    # — baseline (no CCM) performance —
    rmse_raw_train = np.sqrt(np.mean((raw_train - tgt_train)**2))
    rmse_raw_test  = np.sqrt(np.mean((raw_test  - tgt_test )**2))
    r2_raw_train   = r2_score(tgt_train, raw_train, multioutput='uniform_average')
    r2_raw_test    = r2_score(tgt_test,  raw_test,  multioutput='uniform_average')

    # 5) train CCM
    M = compute_color_correction_matrix(raw_train, tgt_train)
    np.save(ccm_npy, M)
    print(f"\nSaved colour correction matrix to '{ccm_npy}'")

    # — CCM performance on train set —
    pred_train = raw_train @ M.T
    # clip predictions to [0,255]
    pred_train = np.clip(pred_train, 0, 255)

    rmse_ccm_train = np.sqrt(np.mean((pred_train - tgt_train)**2))
    r2_ccm_train   = r2_score(tgt_train, pred_train, multioutput='uniform_average')

    # — CCM performance on test set —
    pred_test = raw_test @ M.T
    # clip predictions to [0,255]
    pred_test = np.clip(pred_test, 0, 255)

    rmse_ccm_test = np.sqrt(np.mean((pred_test - tgt_test)**2))
    r2_ccm_test   = r2_score(tgt_test, pred_test, multioutput='uniform_average')

    # 6) build summary table and save to CSV
    summary = pd.DataFrame([
        {'stage': 'raw-train', 'RMSE': rmse_raw_train, 'R2': r2_raw_train},
        {'stage': 'raw-test',  'RMSE': rmse_raw_test,  'R2': r2_raw_test},
        {'stage': 'ccm-train', 'RMSE': rmse_ccm_train, 'R2': r2_ccm_train},
        {'stage': 'ccm-test',  'RMSE': rmse_ccm_test,  'R2': r2_ccm_test},
    ])
    summary.to_csv(metrics_csv, index=False)
    print(summary)
    print(f"Saved performance summary to '{metrics_csv}'")

    # 7) save full datasets and predictions for later viz
    np.savez_compressed(
        data_npz,
        raw_samples=raw_samples,
        target_samples=target_samples,
        raw_train=raw_train,
        tgt_train=tgt_train,
        pred_train=pred_train,
        raw_test=raw_test,
        tgt_test=tgt_test,
        pred_test=pred_test,
    )
    print(f"Saved raw/target/predicted arrays to '{data_npz}'")

if __name__ == "__main__":
    
    raw_csv = 'files/spreadsheets/s5_rgb_normalised.csv'
    target_csv = 'files/spreadsheets/target_data.csv'
    CLK_csv = 'files/key_light_levels/light_levels_CLK.csv'
    ccm_npy = 'files/models/CCM.npy'
    metrics_csv = 'files/spreadsheets/metrics.csv'
    data_npz = 'files/models/data.npz'
    main(raw_csv, CLK_csv, target_csv, ccm_npy, metrics_csv, data_npz)