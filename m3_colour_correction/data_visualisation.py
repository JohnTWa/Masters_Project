import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_channel_scatter(raw, target, pred=None):
    """
    raw, target, pred: each (N,3) arrays.
    Points are plotted channel-wise (raw vs. target and optionally pred vs. target),
    and colored by the *actual* target RGB color.
    """
    channels = ['R', 'G', 'B']
    # Normalize target colors to [0,1] for matplotlib
    target_colors = np.clip(target / 255.0, 0.0, 1.0)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for i, ax in enumerate(axes):
        # Raw vs. target, colored by true target color
        ax.scatter(
            raw[:, i], target[:, i],
            c=target_colors,
            s=20, alpha=0.8,
            label='raw → target'
        )
        # Optional: overlay predictions
        if pred is not None:
            ax.scatter(
                pred[:, i], target[:, i],
                c=target_colors,
                s=20, marker='x', alpha=0.8,
                label='ccm → target'
            )
        ax.set_xlabel(f"{channels[i]} input")
        ax.set_ylabel(f"{channels[i]} target")
        ax.set_title(f"{channels[i]} channel")
        ax.legend(loc='best', fontsize='small')
        ax.set_aspect('equal', 'box')

    plt.tight_layout()
    plt.show()

def inverse_gamma(raw, gamma=2.2):
    """
    Apply a simple power‐law inverse gamma to 0–255 RGB values.
    """
    raw_norm = raw / 255.0
    lin = np.power(raw_norm, gamma)
    return lin * 255.0

def plot_gamma_comparison(raw, target, gamma=2.2):
    """
    Compare channel-wise scatter before and after inverse gamma.
    raw, target: arrays shape (N,3) with values in [0,255].
    """
    channels = ['R','G','B']
    raw_lin = inverse_gamma(raw, gamma=gamma)
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    
    # Top row: original raw vs target
    for i, ax in enumerate(axes[0]):
        ax.scatter(raw[:, i], target[:, i], s=5, alpha=0.5)
        ax.set_title(f'{channels[i]}: raw vs target')
        ax.set_xlabel('raw')
        ax.set_ylabel('target')
        ax.set_aspect('equal', 'box')
    
    # Bottom row: linearized raw vs target
    for i, ax in enumerate(axes[1]):
        ax.scatter(raw_lin[:, i], target[:, i], s=5, alpha=0.5, color='C1')
        ax.set_title(f'{channels[i]}: linearized vs target')
        ax.set_xlabel('inverse‐gamma raw')
        ax.set_ylabel('target')
        ax.set_aspect('equal', 'box')
    
    plt.tight_layout()
    plt.show()

def plot_residuals(pred, target):
    fig, axes = plt.subplots(1, 3, figsize=(12,4))
    channels = ['R','G','B']
    for i, ax in enumerate(axes):
        res = pred[:,i] - target[:,i]
        ax.hist(res, bins=50, alpha=0.7)
        ax.set_title(f"{channels[i]} residuals\n(μ={res.mean():.1f}, σ={res.std():.1f})")
        ax.set_xlabel("Error value")
        ax.set_ylabel("Count")
    plt.tight_layout()
    plt.show()

def plot_3d(raw, target, pred=None):
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(*raw.T, c=np.linalg.norm(raw-target, axis=1), s=20, cmap='inferno')
    ax.set_xlabel('R'); ax.set_ylabel('G'); ax.set_zlabel('B')
    fig.colorbar(sc, label='raw→target Euclidean error')
    plt.show()

    if pred is not None:
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(*pred.T, c=np.linalg.norm(pred-target, axis=1), s=20, cmap='viridis')
        ax.set_xlabel('R'); ax.set_ylabel('G'); ax.set_zlabel('B')
        fig.colorbar(sc, label='ccm→target Euclidean error')
        plt.show()

def plot_rgb_hexbins(raw, target, pred, gridsize=50):
    """
    Plot 3×3 hex-bin density grids for target, raw, and predicted RGB points.
    
    Rows:   [ target, raw, pred ]
    Cols:   [ R vs G,  G vs B,  R vs B ]
    """
    datasets = [
        (target, 'Target'),
        (raw,    'Raw'),
        (pred,   'Predicted')
    ]
    planes = [
        (0, 1, 'R', 'G'),
        (1, 2, 'G', 'B'),
        (0, 2, 'R', 'B')
    ]

    fig, axes = plt.subplots(3, 3, figsize=(15, 15), 
                             sharex='col', sharey='row')
    
    # First pass: compute all counts to find global vmin/vmax (log scale)
    all_counts = []
    for data, _ in datasets:
        for i, j, _, _ in planes:
            counts, xedges, yedges = np.histogram2d(
                data[:, i], data[:, j],
                bins=gridsize, range=[[0,255],[0,255]]
            )
            all_counts.append(counts)
    # Flatten and take log
    log_counts = np.log1p(np.concatenate([c.ravel() for c in all_counts]))
    vmin, vmax = log_counts.min(), log_counts.max()

    # Now actually plot
    for row, (data, dname) in enumerate(datasets):
        for col, (i, j, ci, cj) in enumerate(planes):
            ax = axes[row, col]
            hb = ax.hexbin(
                data[:, i], data[:, j],
                gridsize=gridsize,
                extent=(0,255,0,255),
                cmap='inferno',
                norm=plt.cm.colors.LogNorm(vmin=np.expm1(vmin),
                                           vmax=np.expm1(vmax))
            )
            if row == 0:
                ax.set_title(f"{ci} vs {cj}")
            if col == 0:
                ax.set_ylabel(f"{dname}\n{cj}", rotation=0, labelpad=30)
            if row == 2:
                ax.set_xlabel(ci)
            # lightly draw the 45° line for reference
            ax.plot([0,255],[0,255], color='white', lw=1, alpha=0.3)

    # single colorbar on the right
    cbar = fig.colorbar(hb, ax=axes.ravel().tolist(), 
                        orientation='vertical', fraction=0.02, pad=0.01)
    cbar.set_label('Log(count+1)')

    plt.tight_layout()
    plt.show()

def plot_rgb_clouds_3d(raw, target, pred):
    """
    Displays target, raw (error-colored), and predicted (error-colored)
    RGB point clouds in a single figure with three subplots, using the same
    'inferno' colormap range for raw and predicted errors.
    """
    # Compute Euclidean errors
    err_raw  = np.linalg.norm(raw    - target, axis=1)
    err_pred = np.linalg.norm(pred   - target, axis=1)

    # Determine a common color scale
    vmin = 0.0
    vmax = max(err_raw.max(), err_pred.max())

    fig = plt.figure(figsize=(18, 6))

    # 1) Target
    ax1 = fig.add_subplot(1, 3, 1, projection='3d')
    ax1.scatter(*target.T, s=20, color='gray', alpha=0.6)
    ax1.set_title('Target RGB Points')
    ax1.set_xlabel('R'); ax1.set_ylabel('G'); ax1.set_zlabel('B')

    # 2) Raw points with error coloring
    ax2 = fig.add_subplot(1, 3, 2, projection='3d')
    sc2 = ax2.scatter(*raw.T, c=err_raw, cmap='inferno',
                      vmin=vmin, vmax=vmax, s=20)
    ax2.set_title('Raw RGB Points\n(colored by error)')
    ax2.set_xlabel('R'); ax2.set_ylabel('G'); ax2.set_zlabel('B')
    cbar2 = fig.colorbar(sc2, ax=ax2, shrink=0.6, pad=0.1)
    cbar2.set_label('Euclidean error to target')

    # 3) Predicted points with error coloring
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    sc3 = ax3.scatter(*pred.T, c=err_pred, cmap='inferno',
                      vmin=vmin, vmax=vmax, s=20)
    ax3.set_title('Predicted RGB Points\n(colored by error)')
    ax3.set_xlabel('R'); ax3.set_ylabel('G'); ax3.set_zlabel('B')
    cbar3 = fig.colorbar(sc3, ax=ax3, shrink=0.6, pad=0.1)
    cbar3.set_label('Euclidean error to target')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # # load metrics
    # import pandas as pd
    # df = pd.read_csv('files/spreadsheets/metrics.csv')
    # print(df)

    # load data arrays
    import numpy as np
    data = np.load('files/models/data.npz')
    raw_train   = data['raw_train']
    tgt_train   = data['tgt_train']
    pred_train  = data['pred_train']

    plot_channel_scatter(raw_train, tgt_train)
    plot_gamma_comparison(raw_train, tgt_train)
    plot_residuals(pred_train, tgt_train)
    plot_rgb_hexbins(raw_train, tgt_train, pred_train)
    plot_rgb_clouds_3d(raw_train, tgt_train, pred_train)