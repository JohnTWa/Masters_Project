import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(6, 4))

# Transmitter box
tx = patches.Rectangle((0, 0.5), width=1, height=1, fill=False, edgecolor='black')
ax.add_patch(tx)
ax.text(0.5, 1, "Transmitter", ha='center', va='bottom')

# Receiver box
rx = patches.Rectangle((4, 0.5), width=1, height=1, fill=False, edgecolor='black')
ax.add_patch(rx)
ax.text(4.5, 1, "Receiver", ha='center', va='bottom')

# Example lines
ax.annotate("EN", xy=(1, 1.2), xytext=(4, 1.2),
            arrowprops=dict(arrowstyle="->"))
ax.annotate("CLK", xy=(1, 1.0), xytext=(4, 1.0),
            arrowprops=dict(arrowstyle="->"))
ax.annotate("DATA0", xy=(1, 0.8), xytext=(4, 0.8),
            arrowprops=dict(arrowstyle="->"))

ax.set_xlim(-1, 6)
ax.set_ylim(0, 2.5)
plt.axis('off')
plt.show()