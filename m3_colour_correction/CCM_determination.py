import numpy as np
import pandas as pd
import joblib
from _SETUP_ import set_directory
set_directory()
from common.reset import reset
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from m4_demodulation_and_decoding.edge_detection import detect_edges_with_orig_index

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
    X, *_ = np.linalg.lstsq(raw, target, rcond=None)
    return X.T

def main(raw_csv, CLK_csv, target_csv,
         ccm_npy, ols_joblib, rf_joblib,
         metrics_csv, data_npz,
         test_size=0.2, random_state=19450716112921):
    # 1) Edge sampling
    reset(CLK_csv)
    CLK = detect_edges_with_orig_index(raw_csv, 0, CLK_csv, threshold_fraction=0.2)

    # 2) Load & align
    raw_samples    = load_raw_data(raw_csv, CLK)
    target_samples = load_target_data(target_csv)
    n_raw, n_tgt = raw_samples.shape[0], target_samples.shape[0]
    if n_raw != n_tgt:
        n_keep = min(n_raw, n_tgt)
        print(f"WARNING: truncating to {n_keep} samples (raw={n_raw}, tgt={n_tgt})")
        raw_samples    = raw_samples[-n_keep:]
        target_samples = target_samples[-n_keep:]

    # 3) Split
    raw_tr, raw_te, tgt_tr, tgt_te = train_test_split(
        raw_samples, target_samples,
        test_size=test_size, random_state=random_state
    )

    # 4) Train models
    models = {}

    # 4a) CCM
    M = compute_color_correction_matrix(raw_tr, tgt_tr)
    print("\n=== CCM parameters (3×3 matrix) ===")
    print(M)
    models['CCM'] = ('ccm', M)

    # 4b) OLS
    ols = LinearRegression(fit_intercept=True)
    ols.fit(raw_tr, tgt_tr)
    print("\n=== OLS parameters ===")
    print("Coefficients (shape [n_targets×n_features]):")
    print(ols.coef_)
    print("Intercepts (one per target channel):")
    print(ols.intercept_)
    models['OLS'] = ('ols', ols)

    # 4c) Random Forest
    rf = RandomForestRegressor(
        n_estimators=100,
        random_state=int(random_state/100000),
        n_jobs=-1
    )
    rf.fit(raw_tr, tgt_tr)
    print("\n=== Random Forest parameters ===")
    print("Feature importances (averaged over all trees and outputs):")
    print(rf.feature_importances_)
    models['RF'] = ('rf', rf)

    # 5) Evaluate & save
    records = []
    for name, (key, mdl) in models.items():
        # choose prediction function
        if name == 'CCM':
            def predict_fn(X, M=mdl):
                return np.clip(X @ M.T, 0, 255)
        else:
            def predict_fn(X, model=mdl):
                return np.clip(model.predict(X), 0, 255)

        # train metrics
        p_tr = predict_fn(raw_tr)
        rmse_tr = np.sqrt(np.mean((p_tr - tgt_tr)**2))
        r2_tr   = r2_score(tgt_tr, p_tr, multioutput='uniform_average')
        records.append({'model': name, 'stage': 'train', 'RMSE': rmse_tr, 'R2': r2_tr})

        # test metrics
        p_te = predict_fn(raw_te)
        rmse_te = np.sqrt(np.mean((p_te - tgt_te)**2))
        r2_te   = r2_score(tgt_te, p_te, multioutput='uniform_average')
        records.append({'model': name, 'stage': 'test', 'RMSE': rmse_te, 'R2': r2_te})

        # save
        if name == 'CCM':
            np.save(ccm_npy, mdl)
            print(f"Saved CCM → {ccm_npy}")
        else:
            path = ols_joblib if name=='OLS' else rf_joblib
            joblib.dump(mdl, path)
            print(f"Saved {name} → {path}")

    # 6) Save metrics table
    dfm = pd.DataFrame.from_records(records)
    dfm.to_csv(metrics_csv, index=False)
    print(f"\nSaved metrics:\n{dfm}\n→ {metrics_csv}")

    # 7) Save data for viz
    np.savez_compressed(
        data_npz,
        raw_samples=raw_samples,
        target_samples=target_samples,
        raw_train=raw_tr,  tgt_train=tgt_tr,  pred_train=p_tr,
        raw_test= raw_te,  tgt_test= tgt_te,  pred_test= p_te,
    )
    print(f"Saved data for viz → {data_npz}")

if __name__ == "__main__":
    raw_csv        = 'files/spreadsheets/s5_rgb_normalised.csv'
    target_csv     = 'files/spreadsheets/target_data.csv'
    CLK_csv        = 'files/key_light_levels/light_levels_CLK.csv'
    ccm_npy        = 'files/models/CCM.npy'
    ols_joblib     = 'files/models/OLS.joblib'
    rf_joblib      = 'files/models/RF.joblib'
    metrics_csv    = 'files/spreadsheets/metrics_all_models.csv'
    data_npz       = 'files/models/data_all_models.npz'

    main(raw_csv, CLK_csv, target_csv,
         ccm_npy, ols_joblib, rf_joblib,
         metrics_csv, data_npz)