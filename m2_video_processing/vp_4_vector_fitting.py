import sys
import os
import xml.etree.ElementTree as ET
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

class VectorOverlayApp(QMainWindow):
    def __init__(self, svg_path, image_path, output_svg_path):
        super().__init__()
        self.svg_path = svg_path
        self.image_path = image_path
        self.output_svg_path = output_svg_path  # Path to save modified SVG

        # Load the background image
        self.background_image = QPixmap(image_path)

        self.image_width = self.background_image.width()
        self.image_height = self.background_image.height()

        # Load the SVG using QSvgRenderer
        self.svg_renderer = QSvgRenderer(svg_path)

        # Initialize movement and scaling variables
        self.start_point = None
        self.end_point = None
        self.moving_overlay = False
        self.stretching_overlay = False
        self.scale_width = 1.0
        self.scale_height = 1.0
        self.offset_x = 0  # Movement offset for the X-axis
        self.offset_y = 0  # Movement offset for the Y-axis

        # Set up the main window with a larger margin for the keyboard size
        self.setWindowTitle("Move and Stretch SVG Overlay")
        margin = 300  # Increased margin for a larger window size
        self.setGeometry(100, 100, self.image_width + margin, self.image_height + margin)

        self.overlay_image = QPixmap(self.image_width, self.image_height)
        self.overlay_image.fill(Qt.transparent)

        # QLabel for displaying the combined image
        self.label = QLabel(self)
        self.label.setPixmap(self.background_image)
        self.label.setGeometry(0, 0, self.image_width, self.image_height)

        # Track mouse events
        self.label.mousePressEvent = self.mouse_press_event
        self.label.mouseMoveEvent = self.mouse_move_event
        self.label.mouseReleaseEvent = self.mouse_release_event

    def mouse_press_event(self, event):
        # Capture the initial mouse click position
        self.start_point = event.pos()

        if event.button() == Qt.LeftButton:
            # Left-click starts movement
            self.moving_overlay = True
        elif event.button() == Qt.RightButton:
            # Right-click starts res izing
            self.stretching_overlay = True

    def mouse_move_event(self, event):
        if self.start_point:
            if self.moving_overlay:
                # Calculate the new offset to move the overlay
                self.offset_x += event.pos().x() - self.start_point.x()
                self.offset_y += event.pos().y() - self.start_point.y()
                self.start_point = event.pos()  # Update the starting point for smooth dragging
                self.update_overlay()

            elif self.stretching_overlay:
                # Calculate new scale factors based on mouse drag for stretching
                self.end_point = event.pos()
                self.scale_width = (self.end_point.x() - self.offset_x) / self.image_width
                self.scale_height = (self.end_point.y() - self.offset_y) / self.image_height
                self.update_overlay()

    def mouse_release_event(self, event):
        # Reset points and flags when the mouse is released
        self.start_point = None
        self.end_point = None
        self.moving_overlay = False
        self.stretching_overlay = False

        # Save the final overlay after user interaction
        self.save_overlay()

    def update_overlay(self):
        # Clear the overlay image
        self.overlay_image.fill(Qt.transparent)

        # Create a painter to draw the scaled SVG onto the overlay image
        painter = QPainter(self.overlay_image)

        # Define the scaling based on user dragging, and apply the offset for movement
        new_width = self.image_width * self.scale_width
        new_height = self.image_height * self.scale_height
        scaled_svg_rect = QRectF(self.offset_x, self.offset_y, new_width, new_height)

        # Render the SVG with the new scaling and position (offset)
        self.svg_renderer.render(painter, scaled_svg_rect)
        painter.end()

        # Combine the background and overlay images
        final_image = QPixmap(self.background_image)
        painter = QPainter(final_image)
        painter.drawPixmap(0, 0, self.overlay_image)
        painter.end()

        # Update the QLabel with the combined final image (background + overlay)
        self.label.setPixmap(final_image)

    def save_overlay(self):
        # After modifying the overlay, we will save the updated mesh as an SVG file
        # Parse the original SVG and update the key areas based on new positions and scales
        tree = ET.parse(self.svg_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # Iterate over each "rect" element in the SVG (assuming keys are rectangles)
        for rect in root.findall('.//svg:rect', namespaces):
            x = float(rect.attrib['x']) * self.scale_width + self.offset_x
            y = float(rect.attrib['y']) * self.scale_height + self.offset_y
            width = float(rect.attrib['width']) * self.scale_width
            height = float(rect.attrib['height']) * self.scale_height

            # Update the attributes with the new scaled positions and sizes
            rect.set('x', str(x))
            rect.set('y', str(y))
            rect.set('width', str(width))
            rect.set('height', str(height))

        # Write the modified SVG to the output file
        tree.write(self.output_svg_path)

def vector_fitting(svg_path, image_path, output_svg_path):
    app = QApplication(sys.argv)
    window = VectorOverlayApp(svg_path, image_path, output_svg_path)
    window.show()

    # Start the event loop but do not terminate the script when closing the window
    app.exec_()

# Example usage:

# warped_image_path = 'files/i2_warped_image.jpg'
# mesh_vector_path = 'files/v1_mesh.svg'
# fitted_vector_path = 'files/v2_fitted_mesh.svg'  # Save the fitted vector to this file

# vector_fitting(mesh_vector_path, warped_image_path, fitted_vector_path)