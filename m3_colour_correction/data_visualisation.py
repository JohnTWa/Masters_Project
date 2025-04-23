import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
from scipy.stats import gaussian_kde

def plot_channel_scatter(raw, target, pred):
    """
    Plots two rows of channel-wise scatter plots:
      - Top row: raw vs. target for R, G, B channels
      - Bottom row: predicted vs. target for R, G, B channels
    Points are colored by the true target RGB color.
    """
    channels = ['R', 'G', 'B']
    # Normalize target colors to [0,1]
    target_colors = np.clip(target / 255.0, 0.0, 1.0)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharex='col', sharey='row')
    fig.subplots_adjust(hspace=0.3, wspace=0.2)

    # Top row: raw vs target
    for i in range(3):
        ax = axes[0, i]
        ax.scatter(
            raw[:, i], target[:, i],
            c=target_colors, s=20, alpha=0.8
        )
        ax.set_title(f"Raw {channels[i]} vs Target")
        ax.set_xlabel(f"{channels[i]} raw")
        ax.set_ylabel(f"{channels[i]} target")
        ax.set_aspect('equal', 'box')

    # Bottom row: predicted vs target
    for i in range(3):
        ax = axes[1, i]
        ax.scatter(
            pred[:, i], target[:, i],
            c=target_colors, s=20, alpha=0.8
        )
        ax.set_title(f"Predicted {channels[i]} vs Target")
        ax.set_xlabel(f"{channels[i]} pred")
        ax.set_ylabel(f"{channels[i]} target")
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
    
def plot_rgb_error_planes(raw, target, pred, dot_size=5, alpha=0.7):
    """
    3×3 scatter of RGB planes:
      rows → [Target (gray), Raw (error), Predicted (error)]
      cols → [R vs G, G vs B, R vs B]
    Raw/pred points colored by Euclidean error to target using 'inferno'.
    Each subplot has both X and Y axes labeled.
    """
    # Compute pointwise Euclidean errors
    err_raw  = np.linalg.norm(raw    - target, axis=1)
    err_pred = np.linalg.norm(pred   - target, axis=1)

    # Shared colormap limits
    vmin, vmax = 0.0, max(err_raw.max(), err_pred.max())

    datasets = [
        (target,    'Target',    None),
        (raw,       'Raw',       err_raw),
        (pred,      'Predicted', err_pred)
    ]
    planes = [
        (0, 1, 'R', 'G'),
        (1, 2, 'G', 'B'),
        (0, 2, 'R', 'B')
    ]

    fig, axes = plt.subplots(3, 3, figsize=(15, 15),
                             sharex='col', sharey='row')
    fig.subplots_adjust(right=0.85, top=0.95, bottom=0.05)

    for row, (data, label, errors) in enumerate(datasets):
        for col, (i, j, ci, cj) in enumerate(planes):
            ax = axes[row, col]

            if errors is None:
                # Target row: neutral gray
                ax.scatter(data[:,i], data[:,j],
                           color='gray', s=dot_size, alpha=0.6)
            else:
                sc = ax.scatter(data[:,i], data[:,j],
                                c=errors, cmap='inferno',
                                vmin=vmin, vmax=vmax,
                                s=dot_size, alpha=alpha)
                # Add colorbar only once
                if row == 1 and col == 2:
                    cbar = fig.colorbar(sc, ax=axes.ravel().tolist(),
                                        orientation='vertical',
                                        fraction=0.02, pad=0.02)
                    cbar.set_label('Euclidean error')

            # 45° reference line
            ax.plot([0,255], [0,255], color='white', lw=1, alpha=0.3)

            # Titles for plane names on top row
            if row == 0:
                ax.set_title(f"{ci} vs {cj}", pad=10)
            # Label dataset name at left of each row
            if col == 0:
                ax.annotate(label, xy=(-0.3, 0.5),
                            xycoords='axes fraction',
                            rotation=90, va='center', fontsize=12)

            # Always label axes
            ax.set_xlabel(ci)
            ax.set_ylabel(cj)

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

    plot_channel_scatter(raw_train, tgt_train, pred_train)
    plot_residuals(pred_train, tgt_train)
    plot_rgb_error_planes(raw_train, tgt_train, pred_train)
    plot_rgb_clouds_3d(raw_train, tgt_train, pred_train)