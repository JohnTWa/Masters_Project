from _SETUP_ import set_directory
set_directory()

from common.hamming_code import hamming_encode
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import math

def display_asynchronous_text_timing_diagram_labelled(
    binary_message_strings: list,
    message_labels: list,
    idle_zone_length: int,
    major_fontsize: int, 
    minor_fontsize: int,
    label_bits: bool = True,
):
    """
    Displays text character frames with labeled bits and message labels. 
    """

    start_bit_label = "Start Bit"
    end_bit_label = "End Bit"

    try:
        # Add start and end bits to each message
        binary_frames = [f"1{frame}1" for frame in binary_message_strings]

        idle_period = "0" * idle_zone_length

        transmission_segments = [idle_period]  # Idle zone before the first message
        for msg in binary_frames:
            transmission_segments.append(msg)         # The message itself
            transmission_segments.append(idle_period)  # Idle zone after the message
        transmission = "".join(transmission_segments)
        transmission_length = len(transmission)

        # Create y-values for the binary transmission
        y_values = [int(bit) for bit in transmission]

        # Create x-values for plotting (each bit duration is 1/bit_rate seconds)
        x_values = list(range(0, len(y_values)))

        # Plot the binary transmission scheme
        plt.figure(figsize=(12, 4))
        plt.step(x_values, y_values, where='post', color='black')
        plt.ylim(-0.5, 1.5)
        plt.xticks(fontsize=major_fontsize)
        plt.yticks([0, 1], ["OFF", "ON"], fontsize=major_fontsize)  # Changed here
        plt.grid(False)
        plt.xlabel("Bit Position", fontsize=major_fontsize)
        plt.ylabel("LED State", fontsize=major_fontsize)

        ax = plt.gca()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=16))
        xticks = ax.get_xticks()
        filtered_xticks = [tick for tick in xticks if tick <= len(transmission)-1 and tick >= 0]
        ax.set_xticks(filtered_xticks)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines.bottom.set_bounds(0, transmission_length-1)
        ax.spines.left.set_bounds(0, 1)

        # Label bits and messages
        current_x = idle_zone_length 
        for i, frame in enumerate(binary_frames):
            if label_bits:
                # Label the start bit
                plt.text(
                    current_x + 0.5,
                    int(frame[0]) - 0.5,  # Slightly higher than regular bit labels
                    start_bit_label,
                    ha="center",
                    va="center",
                    fontsize=minor_fontsize,
                    color="black",
                    rotation=90,
                )
                current_x += 1

                # Label each bit in the message (excluding start and end bits)
                for bit in frame[1:-1]:  # Exclude start and end bits
                    plt.text(
                        current_x + 0.5,
                        int(bit) + 0.05,
                        bit,
                        ha="center",
                        fontsize=minor_fontsize,
                    )
                    current_x += 1

                # Label the end bit
                plt.text(
                    current_x + 0.5,
                    int(frame[-1]) - 0.5,  # Slightly higher than regular bit labels
                    end_bit_label,
                    ha="center",
                    va="center",
                    fontsize=minor_fontsize,
                    color="black",
                    rotation=90,
                )
                current_x += 1

            else: 
                current_x += len(frame)

            # Label the message character slightly above the message
            plt.text(
                current_x - len(frame) * 0.5,
                1.35,  # Slightly above bit labels
                message_labels[i],
                ha="center",
                fontsize=major_fontsize*1.5,
                fontweight="bold",  # Bold font
                color="black",
            )

            # Move past the idle zone
            current_x += idle_zone_length

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error: {e}")

def display_asynchronous_text_timing_diagram_labelled_Hamming(
    binary_message_strings: list,
    message_labels: list,
    idle_zone_length: int,
    major_fontsize: int,
    minor_fontsize: int,
    start_bit_label: str = "Start Bit",
    end_bit_label: str = "End Bit",
):
    try:
        # Add start and end bits to each message
        binary_frames = [f"1{msg}1" for msg in binary_message_strings]

        # Construct the idle zone string based on the specified length
        idle_period = "0" * idle_zone_length

        # Construct the full transmission with consistent idle zones
        transmission_segments = [idle_period]  # Idle zone before the first message
        for msg in binary_frames:
            transmission_segments.append(msg)         # The message itself
            transmission_segments.append(idle_period)  # Idle zone after the message
        transmission = "".join(transmission_segments)

        # Create y-values for the binary transmission
        y_values = [int(bit) for bit in transmission]

        # Create x-values for plotting (each bit duration is 1/bit_rate seconds)
        x_values = list(range(0, len(y_values)))

        # Plot the binary transmission scheme
        plt.figure(figsize=(12, 4))
        plt.step(x_values, y_values, where='post', color='black')
        
        # Overlay red line segments for parity bits.
        # Compute overall indices corresponding to parity bits.
        parity_indices = []
        current_index = idle_zone_length  # start after initial idle zone
        for frame in binary_frames:
            current_index += 1  # skip start bit
            for idx, bit in enumerate(frame[1:-1], start=1):
                # Check if the bit position (1-indexed) is a power of 2
                if (idx & (idx - 1)) == 0:
                    parity_indices.append(current_index)
                current_index += 1
            current_index += 1  # skip end bit
            current_index += idle_zone_length  # skip idle zone after frame
        
        # For each parity bit, overlay a red horizontal line segment.
        for i in parity_indices:
            # Draw a horizontal red line from x=i to x=i+1 at y-value y_values[i]
            plt.hlines(y=y_values[i], xmin=i, xmax=i+1, colors='red', linewidth=2)
        
        plt.ylim(-0.5, 1.5)
        plt.xticks(fontsize=major_fontsize)
        plt.yticks([0, 1], ["OFF", "ON"], fontsize=major_fontsize)  # Changed here
        plt.grid(False)
        plt.xlabel("Bit Position", fontsize=major_fontsize)
        plt.ylabel("LED State", fontsize=major_fontsize)

        ax = plt.gca()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=16))
        xticks = ax.get_xticks()
        filtered_xticks = [tick for tick in xticks if tick <= len(transmission)-1 and tick >= 0]
        ax.set_xticks(filtered_xticks)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines.left.set_bounds(0, 1)     

        # Label bits and messages
        current_x = idle_zone_length 
        for i, frame in enumerate(binary_frames):
            # Label the start bit
            plt.text(
                current_x + 0.5,
                int(frame[0]) - 0.5,
                start_bit_label,
                ha="center",
                va="center",
                fontsize=minor_fontsize,
                color="black",
                rotation=90,
            )
            current_x += 1

            # Label each bit in the message (excluding start and end bits)
            for idx, bit in enumerate(frame[1:-1], start=1):
                bit_position = idx
                if (bit_position & (bit_position - 1)) == 0 and bit_position != 0:  # Power of 2
                    weight = "bold"
                    color = "red"
                else:
                    weight = "normal"
                    color = "black"
                plt.text(
                    current_x + 1 / 2,
                    int(bit) + 0.05,
                    bit,
                    ha="center",
                    fontsize=minor_fontsize,
                    fontweight=weight,
                    color=color,
                )
                current_x += 1

            # Label the end bit
            plt.text(
                current_x + 1 / 2,
                int(frame[-1]) - 0.5,
                end_bit_label,
                ha="center",
                va="center",
                fontsize=minor_fontsize,
                color="black",
                rotation=90,
            )
            current_x += 1

            # Label the message character slightly above the message
            plt.text(
                current_x - len(frame) * 1 / 2,
                1.35,
                message_labels[i],
                ha="center",
                fontsize=major_fontsize,
                fontweight="bold",
                color="red",
            )

            # Move past the idle zone
            current_x += idle_zone_length
        
        ax.spines.bottom.set_bounds(0, current_x-1)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error: {e}")

display_asynchronous_text_timing_diagram_labelled(['10110001'], [''], idle_zone_length=5, major_fontsize=24, minor_fontsize=20)
display_asynchronous_text_timing_diagram_labelled_Hamming([hamming_encode('10110001')], [''], idle_zone_length=5, major_fontsize=24, minor_fontsize=20)
display_asynchronous_text_timing_diagram_labelled([1101000, 1100101, 1101100, 1101100, 1101111], ['h','e','l','l','o'], idle_zone_length=8, major_fontsize=24, minor_fontsize=8, label_bits=False)