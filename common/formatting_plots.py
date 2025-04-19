import matplotlib.pyplot as plt
import math
import numpy as np

def set_global_figure_parameters(height=7, ratio=1.7, minor_fontsize=18, major_fontsize=24, linewidth=3, markersize=15, markerwidth=2):
    plt.rcParams.update({
        'figure.figsize': (ratio * height, height),
        'figure.facecolor': 'w',
        'axes.facecolor': 'w',
        'axes.edgecolor': 'black',
        'axes.linewidth': 1,
        'axes.labelsize': major_fontsize,
        'xtick.labelsize': minor_fontsize,
        'ytick.labelsize': minor_fontsize,
        'lines.linewidth': linewidth,
        'lines.markersize': markersize,
        'lines.markeredgewidth': markerwidth,
        'font.size': major_fontsize,
        'legend.fontsize': minor_fontsize,
        'grid.color': 'gray',
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        'legend.frameon': False,
        'font.family': 'Times New Roman',
        'mathtext.fontset': 'custom',
        'mathtext.rm': 'Times New Roman',
        'mathtext.it': 'Times New Roman:italic',
        'mathtext.bf': 'Times New Roman:bold'
    })

def format_figure(fig, ax, x_range=None, y_range=None, y_padding_factor=0.2, grid=True, filter_ticks=True, legend=False, ncol_max=3, filter_anomalies=False):
    """
    Format a figure by adjusting axes, legend, limits, and grid.

    Parameters:
        fig (matplotlib.figure.Figure): The figure object.
        ax (matplotlib.axes.Axes): The axes object to format.
        x_range (tuple, optional): Tuple of (xmin, xmax) to set the x-limits.
        y_range (tuple, optional): Tuple of (ymin, ymax) to set the y-limits.
        y_padding_factor (float, optional): Fractional padding added to y-limits.
        grid (bool, optional): Whether to add a grid to the axis.
        filter_ticks (bool, optional): Whether to filter y-ticks to those within y-limits.
        legend (bool, optional): If True, always show the legend.
        ncol_max (int, optional): Maximum number of columns in the legend.
        filter_anomalies (bool, optional): If True, remove any legend entries labeled 'Anomalies'.

    This function removes unnecessary spines, formats the legend (if applicable), and adjusts
    the plot limits and grid as specified.
    """
    # Remove unnecessary spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Retrieve the legend handles and labels
    lines, labels = ax.get_legend_handles_labels()

    # Optionally filter out any entries labeled 'Anomalies' (case-insensitive)
    if filter_anomalies and lines and labels:
        filtered = [(handle, label) for handle, label in zip(lines, labels) if label.lower() != 'anomalies']
        if filtered:
            lines, labels = zip(*filtered)
        else:
            lines, labels = [], []

    if lines and labels:
        # Only display the legend if there is more than one entry or if explicitly requested
        if len(lines) > 1 or legend:
            # Legend is required:
            legend = True
            new_bottom = 0.15 
            pos = ax.get_position()

            # Determine the legend layout based on the number of entries
            if len(lines) > ncol_max:  # two-row legend
                ncol = ncol_max
                new_height = pos.height * 0.92
                legend_y = (new_bottom + new_height) * 1.15
            else:  # single-row legend
                ncol = len(lines)
                new_height = pos.height * 0.95
                legend_y = (new_bottom + new_height) * 1.15

            # Adjust the axis position to make room for the legend
            ax.set_position([pos.x0, new_bottom, pos.width, new_height])

            # Create the legend on the figure rather than the axes
            fig.legend(lines, labels,
                       loc='upper center',
                       bbox_to_anchor=(0.5, legend_y),
                       ncol=ncol)

    # Adjust the y-limits based on all plotted data with some padding.
    if ax.lines and not y_range:
        all_y_data = np.concatenate([line.get_ydata() for line in ax.lines])
        combined_min = np.min(all_y_data)
        combined_max = np.max(all_y_data)
        padding = (combined_max - combined_min) * y_padding_factor
        ax.set_ylim(combined_min - padding, combined_max + padding)
    elif y_range:
        y_min, y_max = y_range
        ax.set_ylim(y_min, y_max)

    # Optionally adjust x-limits if provided.
    if x_range:
        x_min, x_max = x_range
        ax.set_xlim(x_min, x_max)
    
    # Filter y-ticks to only include those within the current y-limits.
    if filter_ticks:
        ylim = ax.get_ylim()
        yticks = ax.get_yticks()
        visible_ticks = [tick for tick in yticks if tick >= ylim[0] and tick <= ylim[1]]
        ax.set_yticks(visible_ticks)
    
    # Add a grid to the axis.
    if grid:
        ax.grid(True)

    if not legend:
        fig.tight_layout()

def format_figure_right_legend(fig, ax, x_range=None, y_range=None, y_padding_factor=0.2, 
                               grid=True, filter_ticks=True, legend=True):
    import numpy as np

    # Remove unnecessary spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Reserve extra space on the right side for the legend.
    # Here, we adjust the subplot parameters so that the axis is shifted to the left.
    fig.subplots_adjust(right=0.7)
    
    # Retrieve legend handles and labels from the axis.
    lines, labels = ax.get_legend_handles_labels()
    if lines and labels:
        if len(lines) > 0 or legend:
            # Create the legend on the right side, stacked vertically (ncol=1)
            fig.legend(lines, labels,
                       loc='center right',
                       bbox_to_anchor=(0.95, 0.5),
                       ncol=1,
                       frameon=False)
    
    # Adjust the y-limits based on all plotted data with some padding.
    if ax.lines and not y_range:
        all_y_data = np.concatenate([line.get_ydata() for line in ax.lines])
        combined_min = np.min(all_y_data)
        combined_max = np.max(all_y_data)
        padding = (combined_max - combined_min) * y_padding_factor
        ax.set_ylim(combined_min - padding, combined_max + padding)
    elif y_range:
        y_min, y_max = y_range
        ax.set_ylim(y_min, y_max)
    
    # Optionally adjust x-limits if provided.
    if x_range:
        x_min, x_max = x_range
        ax.set_xlim(x_min, x_max)
    
    # Filter y-ticks to only include those within the current y-limits.
    if filter_ticks:
        ylim = ax.get_ylim()
        yticks = ax.get_yticks()
        visible_ticks = [tick for tick in yticks if tick >= ylim[0] and tick <= ylim[1]]
        ax.set_yticks(visible_ticks)
    
    # Add grid to the axis.
    if grid:
        ax.grid(True)
    
    # If no legend is required, use tight_layout to optimize spacing.
    if not legend:
        fig.tight_layout()
    
    return fig, ax

def format_2yaxis_figure(fig, ax_left, ax_right, x_range=None, 
                         y_range_left=None, y_range_right=None, 
                         y_padding_factor=0.2, filter_ticks=True, 
                         legend=False, ncol_max=3, left_color='black', right_color='black'):
    import numpy as np
    
    # Remove unnecessary spines.
    # For left axis, remove top and right spines.
    ax_left.spines['top'].set_visible(False)
    ax_left.spines['right'].set_visible(False)
    # For right axis, remove top and left spines.
    ax_right.spines['top'].set_visible(False)
    ax_right.spines['left'].set_visible(False)
    
    # Set the y-axis label and tick colours.
    ax_left.yaxis.label.set_color(left_color)
    ax_left.tick_params(axis='y', colors=left_color)
    ax_right.yaxis.label.set_color(right_color)
    ax_right.tick_params(axis='y', colors=right_color)
    
    # Combine legend handles and labels from both axes.
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    lines_right, labels_right = ax_right.get_legend_handles_labels()
    combined_lines = lines_left + lines_right
    combined_labels = labels_left + labels_right
    
    if combined_lines and combined_labels:
        # If there is more than one legend entry, or legend was explicitly requested.
        if len(combined_lines) > 1 or legend:
            new_bottom = 0.15 
            pos = ax_left.get_position()
            if len(combined_lines) > ncol_max:  # two-row legend.
                ncol = ncol_max
                new_height = pos.height * 0.92
                legend_y = (new_bottom + new_height) * 1.15
            else:  # single-row legend.
                ncol = len(combined_lines)
                new_height = pos.height * 0.95
                legend_y = (new_bottom + new_height) * 1.15
            
            # Adjust the left axis position.
            ax_left.set_position([pos.x0, new_bottom, pos.width, new_height])
            
            # Create a combined legend at the upper center of the figure.
            fig.legend(combined_lines, combined_labels,
                       loc='upper center',
                       bbox_to_anchor=(0.5, legend_y),
                       ncol=ncol)
    
    # Adjust the y-limits for the left axis.
    if ax_left.lines and not y_range_left:
        all_y_left = np.concatenate([line.get_ydata() for line in ax_left.lines])
        combined_min_left = np.min(all_y_left)
        combined_max_left = np.max(all_y_left)
        padding_left = (combined_max_left - combined_min_left) * y_padding_factor
        ax_left.set_ylim(combined_min_left - padding_left, combined_max_left + padding_left)
    elif y_range_left:
        y_min_left, y_max_left = y_range_left
        ax_left.set_ylim(y_min_left, y_max_left)
    
    # Adjust the y-limits for the right axis.
    if ax_right.lines and not y_range_right:
        all_y_right = np.concatenate([line.get_ydata() for line in ax_right.lines])
        combined_min_right = np.min(all_y_right)
        combined_max_right = np.max(all_y_right)
        padding_right = (combined_max_right - combined_min_right) * y_padding_factor
        ax_right.set_ylim(combined_min_right - padding_right, combined_max_right + padding_right)
    elif y_range_right:
        y_min_right, y_max_right = y_range_right
        ax_right.set_ylim(y_min_right, y_max_right)
    
    # Adjust x-limits for both axes if provided.
    if x_range:
        x_min, x_max = x_range
        ax_left.set_xlim(x_min, x_max)
        ax_right.set_xlim(x_min, x_max)
    
    # Filter y-ticks to only include those within the current y-limits.
    if filter_ticks:
        for ax in [ax_left, ax_right]:
            ylim = ax.get_ylim()
            yticks = ax.get_yticks()
            visible_ticks = [tick for tick in yticks if tick >= ylim[0] and tick <= ylim[1]]
            ax.set_yticks(visible_ticks)
    
    return fig, ax_left, ax_right

def format_double_figure(fig, ax_top, ax_bottom, x_range=None, 
                         y_range_top=None, y_range_bottom=None, 
                         y_padding_factor=0, grid=True, filter_ticks=True,
                         legend_title_top="Top Legend", legend_title_bottom="Bottom Legend", ncol=1,
                         include_bottom_legend=True, right_margin=0.7):
    
    # Remove unnecessary spines from both axes.
    for ax in [ax_top, ax_bottom]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    # Get and filter legend handles for the top subplot.
    handles_top, labels_top = ax_top.get_legend_handles_labels()
    filtered_handles_top = []
    filtered_labels_top = []
    for handle, label in zip(handles_top, labels_top):
        if not handle.get_visible():
            continue
        if hasattr(handle, 'get_linestyle') and hasattr(handle, 'get_marker'):
            if handle.get_linestyle() not in [None, 'none', 'None'] or handle.get_marker() not in [None, 'none', 'None']:
                filtered_handles_top.append(handle)
                filtered_labels_top.append(label)
    
    # Get and filter legend handles for the bottom subplot.
    handles_bottom, labels_bottom = ax_bottom.get_legend_handles_labels()
    filtered_handles_bottom = []
    filtered_labels_bottom = []
    for handle, label in zip(handles_bottom, labels_bottom):
        if not handle.get_visible():
            continue
        if hasattr(handle, 'get_linestyle') and hasattr(handle, 'get_marker'):
            if handle.get_linestyle() not in [None, 'none', 'None'] or handle.get_marker() not in [None, 'none', 'None']:
                filtered_handles_bottom.append(handle)
                filtered_labels_bottom.append(label)

    # Add legends.
    if include_bottom_legend:
        ax_top.legend(filtered_handles_top, filtered_labels_top, title=legend_title_top,
                      loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol, frameon=False, fontsize=16)
        ax_bottom.legend(filtered_handles_bottom, filtered_labels_bottom, title=legend_title_bottom,
                         loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol, frameon=False, fontsize=16)
    else:
        # Use only the handles and labels from the top subplot to create a single legend.
        fig.legend(filtered_handles_top, filtered_labels_top, title=legend_title_top,
           loc='center right', bbox_to_anchor=(1, 0.5), ncol=ncol, frameon=False, fontsize=16)
    
    # Adjust the subplots to leave space for the legends.
    fig.subplots_adjust(right=right_margin)
    
    # Adjust y-limits for the top axis.
    if ax_top.lines and not y_range_top:
        all_y_top = np.concatenate([line.get_ydata() for line in ax_top.lines])
        combined_min_top = np.min(all_y_top)
        combined_max_top = np.max(all_y_top)
        padding_top = (combined_max_top - combined_min_top) * y_padding_factor
        ax_top.set_ylim(combined_min_top - padding_top, combined_max_top + padding_top)
    elif y_range_top:
        y_min_top, y_max_top = y_range_top
        ax_top.set_ylim(y_min_top, y_max_top)
    
    # Adjust y-limits for the bottom axis.
    if ax_bottom.lines and not y_range_bottom:
        all_y_bottom = np.concatenate([line.get_ydata() for line in ax_bottom.lines])
        combined_min_bottom = np.min(all_y_bottom)
        combined_max_bottom = np.max(all_y_bottom)
        padding_bottom = (combined_max_bottom - combined_min_bottom) * y_padding_factor
        ax_bottom.set_ylim(combined_min_bottom - padding_bottom, combined_max_bottom + padding_bottom)
    elif y_range_bottom:
        y_min_bottom, y_max_bottom = y_range_bottom
        ax_bottom.set_ylim(y_min_bottom, y_max_bottom)
    
    # Adjust x-limits for both axes if provided.
    if x_range:
        x_min, x_max = x_range
        ax_top.set_xlim(x_min, x_max)
        ax_bottom.set_xlim(x_min, x_max)
    
    # Filter y-ticks for both axes.
    if filter_ticks:
        for ax in [ax_top, ax_bottom]:
            ylim = ax.get_ylim()
            yticks = ax.get_yticks()
            visible_ticks = [tick for tick in yticks if tick >= ylim[0] and tick <= ylim[1]]
            ax.set_yticks(visible_ticks)
    
    # Add grid to both axes if requested.
    if grid:
        ax_top.grid(True)
        ax_bottom.grid(True)
    
    return fig, ax_top, ax_bottom

def format_triple_figure(fig, ax_top, ax_mid, ax_bottom, x_range=None, 
                         y_range_top=None, y_range_mid=None, y_range_bottom=None, 
                         y_padding_factor=0, grid=True, filter_ticks=True,
                         legend_title_top="Top Legend", legend_title_mid="Middle Legend", legend_title_bottom="Bottom Legend",
                         ncol=1, include_bottom_legend=True, right_margin=0.7):
    import numpy as np

    # Remove unnecessary spines from all axes.
    for ax in [ax_top, ax_mid, ax_bottom]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Helper function to filter legend entries.
    def filter_legend(ax):
        handles, labels = ax.get_legend_handles_labels()
        filtered_handles = []
        filtered_labels = []
        for handle, label in zip(handles, labels):
            if hasattr(handle, 'get_linestyle') and hasattr(handle, 'get_marker'):
                if handle.get_linestyle() not in [None, 'none', 'None'] or handle.get_marker() not in [None, 'none', 'None']:
                    filtered_handles.append(handle)
                    filtered_labels.append(label)
        return filtered_handles, filtered_labels

    # Filter legend entries for each axis.
    handles_top, labels_top = filter_legend(ax_top)
    handles_mid, labels_mid = filter_legend(ax_mid)
    handles_bottom, labels_bottom = filter_legend(ax_bottom)

    # Add legends.
    if include_bottom_legend:
        ax_top.legend(handles_top, labels_top, title=legend_title_top,
                      loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol, frameon=False, fontsize=16)
        ax_mid.legend(handles_mid, labels_mid, title=legend_title_mid,
                      loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol, frameon=False, fontsize=16)
        ax_bottom.legend(handles_bottom, labels_bottom, title=legend_title_bottom,
                         loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=ncol, frameon=False, fontsize=16)
    else:
        # Combine all handles and labels for one legend.
        combined_handles = handles_top + handles_mid + handles_bottom
        combined_labels = labels_top + labels_mid + labels_bottom
        fig.legend(combined_handles, combined_labels, title=legend_title_top,
                   loc='center right', bbox_to_anchor=(1, 0.5), ncol=ncol, frameon=False, fontsize=16)

    # Adjust the subplots to leave space for the legends.
    fig.subplots_adjust(right=right_margin)

    # Helper to set y-limits with optional padding.
    def adjust_y_limits(ax, y_range):
        if ax.lines and not y_range:
            all_y = np.concatenate([line.get_ydata() for line in ax.lines])
            combined_min = np.min(all_y)
            combined_max = np.max(all_y)
            padding = (combined_max - combined_min) * y_padding_factor
            ax.set_ylim(combined_min - padding, combined_max + padding)
        elif y_range:
            y_min, y_max = y_range
            ax.set_ylim(y_min, y_max)
        return ax

    # Adjust y-limits for each axis.
    ax_top = adjust_y_limits(ax_top, y_range_top)
    ax_mid = adjust_y_limits(ax_mid, y_range_mid)
    ax_bottom = adjust_y_limits(ax_bottom, y_range_bottom)

    # Adjust x-limits for all axes if provided.
    if x_range:
        x_min, x_max = x_range
        for ax in [ax_top, ax_mid, ax_bottom]:
            ax.set_xlim(x_min, x_max)

    # Optionally filter y-ticks for each axis.
    if filter_ticks:
        for ax in [ax_top, ax_mid, ax_bottom]:
            ylim = ax.get_ylim()
            yticks = ax.get_yticks()
            visible_ticks = [tick for tick in yticks if tick >= ylim[0] and tick <= ylim[1]]
            ax.set_yticks(visible_ticks)

    # Add grid if requested.
    if grid:
        for ax in [ax_top, ax_mid, ax_bottom]:
            ax.grid(True)

    return fig, ax_top, ax_mid, ax_bottom
