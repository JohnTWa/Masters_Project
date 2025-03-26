import csv
import xml.etree.ElementTree as ET

def parse_svg(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    key_areas = []

    # Get the viewBox attribute if it exists
    viewBox = root.attrib.get('viewBox', None)

    # Iterate over each "rect" element in the SVG (assuming keys are rectangles)
    for rect in root.findall('.//svg:rect', namespaces):
        x = float(rect.attrib['x'])
        y = float(rect.attrib['y'])
        width = float(rect.attrib['width'])
        height = float(rect.attrib['height'])
        
        # Store the top-left and bottom-right coordinates of each key
        key_areas.append({
            'top_left': (x, y),
            'bottom_right': (x + width, y + height),
            'width': width,
            'height': height
        })

    return key_areas, viewBox

def save_coordinates_to_csv(svg_path, csv_path):
    # Parse the SVG to get key areas and viewBox
    key_areas, viewBox = parse_svg(svg_path)

    # Sort key areas first by y (top to bottom) and then by x (left to right) with a tolerance
    tolerance = 5  # Adjust as needed based on key alignment
    key_areas.sort(key=lambda k: (round(k['top_left'][1] / tolerance), k['top_left'][0]))

    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write viewBox information if available
        if viewBox:
            writer.writerow(['viewBox', viewBox])
        
        # Write header for key data
        writer.writerow(['Key', 'Top Left X', 'Top Left Y', 'Width', 'Height'])
        
        # Number keys in the sorted order, starting from Key 1
        for i, key in enumerate(key_areas, start=1):
            writer.writerow([f'Key_{i}', key['top_left'][0], key['top_left'][1], key['width'], key['height']])
    
    print(f"Key coordinates saved to {csv_path}, ordered from left to right across rows, excluding the outline.")

# Example usage:
# fitted_vector_path = 'files/v2_fitted_mesh.svg'
# coordinates_csv_path = 'files/s1_key_coordinates.csv'
# save_coordinates_to_csv(fitted_vector_path, coordinates_csv_path)