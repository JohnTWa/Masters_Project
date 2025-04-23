from _SETUP_ import set_directory
set_directory()

import sys
import csv
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QApplication, QLabel
import sys
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

###### DISPLAYING IMAGE ######

class ImageDisplayApp(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.setWindowTitle("Image Display")

        # Check if the file is SVG
        if self.image_path.lower().endswith('.svg'):
            # Load SVG and render it into a QPixmap
            svg_renderer = QSvgRenderer(self.image_path)
            width = svg_renderer.defaultSize().width()
            height = svg_renderer.defaultSize().height()
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
        else:
            # Load PNG or JPG
            pixmap = QPixmap(self.image_path)
            width = pixmap.width()
            height = pixmap.height()

        # Set the window size to match the image size
        self.setGeometry(100, 100, width, height)

        # QLabel to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, width, height)

def display_image(image_path):
    app = QApplication(sys.argv)
    window = ImageDisplayApp(image_path)
    window.show()
    app.exec_()

###### RECONSTRUCTING SVG ######

def reconstruct_svg(csv_path, output_svg_path):
    # Create the SVG root element with default attributes
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")

    # Open and read the CSV file
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        
        # Read the viewBox row if it exists
        first_row = next(reader)
        if first_row[0] == 'viewBox':
            svg.set('viewBox', first_row[1])
            header_row = next(reader)  # Move to the next row, which is the header
        else:
            header_row = first_row  # First row is the header if no viewBox

        # Iterate over the remaining rows to read rectangle data
        for index, row in enumerate(reader, start=1):
            key_label, top_left_x, top_left_y, width, height = row
            
            # Create a new rectangle element with the CSV data
            rect = ET.Element(
                'rect',
                x=top_left_x,
                y=top_left_y,
                width=width,
                height=height,
                style="fill:none;stroke:black;stroke-width:1"
            )
            svg.append(rect)
            
            # Create a text element for the key number in the top-left corner of the rectangle
            text = ET.Element(
                'text',
                x=top_left_x,
                y=str(float(top_left_y) + 10),  # Adjust the y-position to offset the text slightly inside the rectangle
                fill="black",
                style="font-size:10px;font-family:Arial"
            )
            text.text = str(index)  # Set the text to the key number
            svg.append(text)

    # Write the reconstructed SVG to file
    tree = ET.ElementTree(svg)
    tree.write(output_svg_path)

    print(f"SVG reconstructed and saved to {output_svg_path}")

###### OVERLAYING IMAGE ######

def produce_overlaid_image(warped_vector_path, input_image_path, overlaid_image_path):
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QPainter
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtCore import Qt

    app = QApplication(sys.argv)

    # Load the input image
    background_image = QPixmap(input_image_path)
    image_width = background_image.width()
    image_height = background_image.height()

    # Load the warped vector SVG using QSvgRenderer
    svg_renderer = QSvgRenderer(warped_vector_path)

    # Prepare the overlay image with a transparent background
    overlay_image = QPixmap(image_width, image_height)
    overlay_image.fill(Qt.transparent)

    # Use QPainter to render the SVG onto the overlay image
    painter = QPainter(overlay_image)
    svg_renderer.render(painter)
    painter.end()

    # Combine the background image with the overlay
    final_image = QPixmap(background_image)
    painter = QPainter(final_image)
    painter.drawPixmap(0, 0, overlay_image)
    painter.end()

    # Save the combined image as a JPG or PNG
    if overlaid_image_path.endswith('.jpg') or overlaid_image_path.endswith('.jpeg'):
        final_image.save(overlaid_image_path, "JPEG")
    else:
        final_image.save(overlaid_image_path, "PNG")

    app.quit()

###### COLOURING KEYBOARD ######

def display_rgb_keyboard(keyboard_vector_path, output_svg_path):
    """
    Colors every rectangle in the given keyboard vector file with a sequence of red, green, blue, and colorless,
    and labels each key in the center.

    Parameters:
    - keyboard_vector_path (str): Path to the SVG file containing the keyboard vector.
    - output_svg_path (str): Path to save the colored SVG file.
    """
    try:
        # Parse the SVG file
        tree = ET.parse(keyboard_vector_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # Define the sequence of colors: red, green, blue, and colorless
        colors = ['#ff0000', '#00ff00', '#0000ff', 'none']  # RGB Hex codes with 'none' for colorless

        # Iterate over each "rect" element in the SVG, assuming each key is represented by a rectangle
        rect_elements = root.findall('.//svg:rect', namespaces)
        for i, rect in enumerate(rect_elements):
            # Assign a color from the sequence based on the index
            color_hex = colors[i % len(colors)]
            # Set the fill color for the rectangle
            rect.set('style', f'fill:{color_hex};stroke:black;stroke-width:1')

            # Add a text element for the index in the center of the rectangle
            x = float(rect.get('x')) + float(rect.get('width')) / 2
            y = float(rect.get('y')) + float(rect.get('height')) / 2
            text = ET.Element('text', {
                'x': str(x),
                'y': str(y),
                'text-anchor': 'middle',
                'dominant-baseline': 'central',
                'font-size': '8',
                'fill': 'black'
            })
            text.text = str(i + 1)
            root.append(text)

        # Save the modified SVG to a new file
        tree.write(output_svg_path)
        print(f"Colored keyboard SVG saved to {output_svg_path}")

    except ET.ParseError as e:
        print(f"Error parsing the SVG file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage:
# display_colours('v3_reconstructed_mesh.svg', 's3_rgb_averages.csv', 'coloured_svg.svg', 2)

def display_rgb_keyboard(keyboard_vector_path, output_svg_path):
    """
    Colors every rectangle in the given keyboard vector file with a sequence of red, green, blue, and colorless.

    Parameters:
    - keyboard_vector_path (str): Path to the SVG file containing the keyboard vector.
    - output_svg_path (str): Path to save the colored SVG file.
    """
    try:
        # Parse the SVG file
        tree = ET.parse(keyboard_vector_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # Define the sequence of colors: red, green, blue, and colorless
        colors = ['#ff0000', '#00ff00', '#0000ff', 'none']  # RGB Hex codes with 'none' for colorless

        # Iterate over each "rect" element in the SVG, assuming each key is represented by a rectangle
        rect_elements = root.findall('.//svg:rect', namespaces)
        for i, rect in enumerate(rect_elements):
            # Assign a color from the sequence based on the index
            color_hex = colors[i % len(colors)]
            # Set the fill color for the rectangle
            rect.set('style', f'fill:{color_hex};stroke:black;stroke-width:1')

        # Save the modified SVG to a new file
        tree.write(output_svg_path)
        print(f"Colored keyboard SVG saved to {output_svg_path}")

    except ET.ParseError as e:
        print(f"Error parsing the SVG file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

display_rgb_keyboard('files/keyboard_vectors/v5_reconstructed_mesh.svg', 'figures/vector.svg')