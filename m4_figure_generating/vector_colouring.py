import csv
import xml.etree.ElementTree as ET

def display_colours(keyboard_svg_path, rgb_csv_path, coloured_svg_path, row_number, tolerance=0.1):
    # Load the RGB averages CSV file
    with open(rgb_csv_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Read the specified row corresponding to the "row_number" argument
        rgb_values = []
        for row_index, row in enumerate(csv_reader):
            if row_index == row_number - 1:  # Select the correct row (0-based indexing)
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
        raise ValueError(f"No data found for the specified row number {row_number}.")

    # Parse the SVG file
    tree = ET.parse(keyboard_svg_path)
    root = tree.getroot()
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # Collect all rect elements
    rects = []
    for elem in root.iter():
        tag = elem.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]  # Strip namespace
        if tag == 'rect':
            rects.append(elem)
    
    # Extract rect positions and sort them
    rect_info = []
    for rect in rects:
        x = float(rect.get('x'))
        y = float(rect.get('y'))
        width = float(rect.get('width'))
        height = float(rect.get('height'))
        rect_info.append({
            'element': rect,
            'x': x,
            'y': y,
            'width': width,
            'height': height
        })

    # Round coordinates according to tolerance
    for info in rect_info:
        info['x'] = round(info['x'] / tolerance) * tolerance
        info['y'] = round(info['y'] / tolerance) * tolerance

    # Sort rects by y (top to bottom), then x (left to right) with row consideration
    rect_info.sort(key=lambda k: (k['y'], k['x']))
    new_row_idx = 0
    previous_y = -float('inf')
    for info in rect_info:
        if abs(info['y'] - previous_y) > 0.2 * info['height']:
            new_row_idx += 1
            previous_y = info['y']
        info['row'] = new_row_idx
    
    # Sort by row first, then by x
    rect_info.sort(key=lambda k: (k['row'], k['x']))

    # Color the rectangles with corresponding RGB values
    for i, info in enumerate(rect_info):
        if i < len(rgb_values):  # Ensure there is a corresponding color value
            avg_r, avg_g, avg_b = rgb_values[i]
            color_hex = f'#{avg_r:02x}{avg_g:02x}{avg_b:02x}'  # Convert RGB to hex format

            # Set the fill color for the rectangle
            info['element'].set('style', f'fill:{color_hex};stroke:black;stroke-width:1')

    # Save the modified SVG to a new file
    tree.write(coloured_svg_path)
    print(f"Coloured SVG saved to {coloured_svg_path}")

def display_rgb_pattern(keyboard_svg_path, coloured_svg_path, tolerance=0.1):

    # Parse the SVG file
    tree = ET.parse(keyboard_svg_path)
    root = tree.getroot()
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # Collect all rect elements
    rects = []
    for elem in root.iter():
        tag = elem.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]  # Strip namespace
        if tag == 'rect':
            rects.append(elem)
    
    # Extract rect positions and sort them
    rect_info = []
    for rect in rects:
        x = float(rect.get('x'))
        y = float(rect.get('y'))
        width = float(rect.get('width'))
        height = float(rect.get('height'))
        rect_info.append({
            'element': rect,
            'x': x,
            'y': y,
            'width': width,
            'height': height
        })

    # Round coordinates according to tolerance
    for info in rect_info:
        info['x'] = round(info['x'] / tolerance) * tolerance
        info['y'] = round(info['y'] / tolerance) * tolerance

    # Sort rects by y (top to bottom), then x (left to right) with row consideration
    rect_info.sort(key=lambda k: (k['y'], k['x']))
    new_row_idx = 0
    previous_y = -float('inf')
    for info in rect_info:
        if abs(info['y'] - previous_y) > 0.2 * info['height']:
            new_row_idx += 1
            previous_y = info['y']
        info['row'] = new_row_idx
    
    # Sort by row first, then by x
    rect_info.sort(key=lambda k: (k['row'], k['x']))

    alternating_colour_set = ('#ff0000', '#00ff00', '#0000ff', '000000')
    colour = []
    for i, ID in enumerate(rect_info):
        _, remainder = divmod(i, len(alternating_colour_set))
        colour = alternating_colour_set[remainder]
        ID['element'].set('style', f'fill:{colour};stroke:black;stroke-width:1')
    
    # Save the modified SVG to a new file
    tree.write(coloured_svg_path)
    print(f"Alternating RGB coloured SVG saved to {coloured_svg_path}")

# Example usage:
display_colours('files/keyboard_vectors/v2_keyboard_tidied.svg', 'files/spreadsheets/s4_rgb_averages.csv', 'files/keyboard_vectors/v6_coloured_mesh.svg', 100)
display_rgb_pattern('files/keyboard_vectors/v2_keyboard_tidied.svg', 'files/keyboard_vectors/v7_coloured_mesh.svg', 0.1)