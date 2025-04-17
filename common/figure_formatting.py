import matplotlib.pyplot as plt

def set_global_font():
    plt.rcParams.update({
        'axes.facecolor': 'w',
        'font.family': 'Times New Roman',
        'mathtext.fontset': 'custom',
        'mathtext.rm': 'Times New Roman',
        'mathtext.it': 'Times New Roman:italic',
        'mathtext.bf': 'Times New Roman:bold'
    })