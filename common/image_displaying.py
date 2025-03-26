import sys
import csv
import xml.etree.ElementTree as ET
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel
import sys
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
import csv
import xml.etree.ElementTree as ET

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

def produce_overlaid_image(
    warped_vector_path,
    input_image_path,
    overlaid_image_path,
    overlay_image_path=None
):
    """
    Combines an input image (background) with an optional warped vector SVG overlay 
    and an optional second overlay image (e.g. a PNG mask).

    Parameters:
    - warped_vector_path (str or None): Path to the SVG file to overlay. If None, no SVG overlay is applied.
    - input_image_path (str): Path to the background image.
    - overlaid_image_path (str): Where to save the final combined image (JPEG or PNG).
    - overlay_image_path (str or None): If provided, path to an additional image overlay. 
                                        Drawn on top of both the background and SVG.
    """
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QPainter
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtCore import Qt

    app = QApplication(sys.argv)

    # 1) Load the background image
    background_image = QPixmap(input_image_path)
    image_width = background_image.width()
    image_height = background_image.height()

    # We'll compose everything onto 'final_image'.
    final_image = QPixmap(background_image)  # start with the background

    # 2) If there's an SVG path, render it
    if warped_vector_path is not None:
        if not warped_vector_path.strip():
            print("SVG path is empty, skipping SVG overlay.")
        else:
            svg_renderer = QSvgRenderer(warped_vector_path)

            # Create a transparent QPixmap for the SVG overlay
            svg_overlay = QPixmap(image_width, image_height)
            svg_overlay.fill(Qt.transparent)

            # Paint the SVG onto the overlay
            painter = QPainter(svg_overlay)
            svg_renderer.render(painter)
            painter.end()

            # Now draw that overlay onto 'final_image'
            painter = QPainter(final_image)
            painter.drawPixmap(0, 0, svg_overlay)
            painter.end()

    # 3) If there's an overlay image, draw it on top
    if overlay_image_path is not None:
        if not overlay_image_path.strip():
            print("Overlay image path is empty, skipping image overlay.")
        else:
            overlay_pixmap = QPixmap(overlay_image_path)
            if not overlay_pixmap.isNull():
                painter = QPainter(final_image)
                painter.drawPixmap(0, 0, overlay_pixmap)
                painter.end()
            else:
                print(f"Warning: Failed to load overlay image from {overlay_image_path}")

    # 4) Save the combined image
    if overlaid_image_path.lower().endswith('.jpg') or overlaid_image_path.lower().endswith('.jpeg'):
        final_image.save(overlaid_image_path, "JPEG")
    else:
        final_image.save(overlaid_image_path, "PNG")

    print(f"Saved overlaid image to {overlaid_image_path}")

    app.quit()

# Example Use:
# produce_overlaid_image("files/keyboard_vectors/figure_keyboard_tidied_fitted.svg", "files/warped_frames/warped_frame_0.png", "files/i3_overlaid.png")

###### COLOURING KEYBOARD ######

def display_colours(reconstructed_svg_path, rgb_csv_path, coloured_svg_path, number):
    # Load the RGB averages CSV file
    with open(rgb_csv_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Read the specified row corresponding to the "number" argument
        rgb_values = []
        for row_index, row in enumerate(csv_reader):
            if row_index == number - 1:  # Select the correct row (0-based indexing)
                if len(row) % 3 != 0:
                    raise ValueError("Each row must contain RGB values in groups of three.")

                # Extract RGB values in triplets
                for i in range(0, len(row), 3):
                    avg_r = int(row[i])
                    avg_g = int(row[i + 1])
                    avg_b = int(row[i + 2])
                    rgb_values.append((avg_r, avg_g, avg_b))
                break  # Stop reading after the desired row is found

    if not rgb_values:
        raise ValueError(f"No data found for the specified row number {number}.")

    # Parse the SVG file
    tree = ET.parse(reconstructed_svg_path)
    root = tree.getroot()
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}

    # Iterate over each "rect" element in the SVG, assuming each key is represented by a rectangle
    rect_elements = root.findall('.//svg:rect', namespaces)
    for i, rect in enumerate(rect_elements):
        if i < len(rgb_values):  # Ensure there is a corresponding color value
            # Get the RGB color for the current key
            avg_r, avg_g, avg_b = rgb_values[i]
            color_hex = f'#{avg_r:02x}{avg_g:02x}{avg_b:02x}'  # Convert RGB to hex format

            # Set the fill color for the rectangle
            rect.set('style', f'fill:{color_hex};stroke:black;stroke-width:1')

    # Save the modified SVG to a new file
    tree.write(coloured_svg_path)
    print(f"Coloured SVG saved to {coloured_svg_path}")

# Example usage:
# display_colours('v3_reconstructed_mesh.svg', 's3_rgb_averages.csv', 'coloured_svg.svg', 2)