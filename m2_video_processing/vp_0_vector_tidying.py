def tidy_keyboard_vector_reorder_rows(keyboard_vector_path, tidied_vector_path, tolerance=0.1, colour='#000000'):
    import xml.etree.ElementTree as ET

    # Parse the SVG file
    tree = ET.parse(keyboard_vector_path)
    root = tree.getroot()
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # Collect all rect elements and their parent references
    rects = []
    for parent in root.iter():
        for elem in list(parent):  # Use list to prevent modification issues while iterating
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]  # Strip namespace
            if tag == 'rect':
                rects.append({'element': elem, 'parent': parent})

    # Extract rect positions and sort them
    rect_info = []
    for rect_data in rects:
        rect = rect_data['element']
        x = float(rect.get('x'))
        y = float(rect.get('y'))
        rect_info.append({
            'element': rect,
            'x': x,
            'y': y,
            'parent': rect_data['parent']
        })

    # Round coordinates according to tolerance
    for info in rect_info:
        info['x'] = round(info['x'] / tolerance) * tolerance
        info['y'] = round(info['y'] / tolerance) * tolerance

    # Sort rects by y (top to bottom), then x (left to right)
    rect_info.sort(key=lambda k: (k['y'], k['x']))

    # Rename IDs consecutively
    for idx, info in enumerate(rect_info, start=1):
        rect = info['element']
        rect.set('id', f'rect{idx}')
        # Update x and y attributes with rounded values
        rect.set('x', str(info['x']))
        rect.set('y', str(info['y']))
        # Set stroke-width to 1 and colour
        style = rect.get('style', '')
        # Ensure stroke-width and colour are set or overwritten
        styles = {s.split(':')[0].strip(): s.split(':')[1].strip() for s in style.split(';') if ':' in s}
        styles['stroke-width'] = '1'
        styles['stroke'] = colour
        new_style = ';'.join(f'{k}:{v}' for k, v in styles.items())
        rect.set('style', new_style)

    # Remove all original rect elements from their parents
    for info in rect_info:
        info['parent'].remove(info['element'])

    # Append the rect elements back in the sorted order
    for info in rect_info:
        root.append(info['element'])

    # Write the reordered SVG to the output path
    tree.write(tidied_vector_path)
    print(f"Tidied and reordered vector saved to {tidied_vector_path}")

# Example usage
tidy_keyboard_vector_reorder_rows('files/keyboard_vectors/v3_fitted_mesh.svg', 'files/keyboard_vectors/figure_keyboard_tidied_fitted.svg')

def add_number_labels_to_svg(keyboard_vector_path, labeled_vector_path, tolerance=0.1):
    import xml.etree.ElementTree as ET

    def should_start_new_row(current_y, previous_y, rect_height):
        # Determine if the new rectangle starts a new row
        return abs(current_y - previous_y) > 0.2 * rect_height

    # Parse the SVG file
    tree = ET.parse(keyboard_vector_path)
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
        if should_start_new_row(info['y'], previous_y, info['height']):
            new_row_idx += 1
            previous_y = info['y']
        info['row'] = new_row_idx

    # Sort by row first, then by x
    rect_info.sort(key=lambda k: (k['row'], k['x']))

    # Rename IDs consecutively and add number labels
    for idx, info in enumerate(rect_info, start=1):
        rect = info['element']
        rect.set('id', f'rect{idx}')

        # Calculate label position (center of the rectangle)
        label_x = info['x'] + info['width'] / 2
        label_y = info['y'] + info['height'] / 2

        # Create a text element to label the rectangle
        text_elem = ET.Element('{http://www.w3.org/2000/svg}text', attrib={
            'x': str(label_x),
            'y': str(label_y),
            'fill': 'black',  # Color of the text
            'font-size': '12',  # Size of the text
            'text-anchor': 'middle',  # Center text horizontally
            'dominant-baseline': 'middle'  # Center text vertically
        })
        text_elem.text = str(idx)

        # Add the text element to the SVG
        root.append(text_elem)

    # Write the labeled SVG to the output path
    tree.write(labeled_vector_path)
    print(f"Labeled vector saved to {labeled_vector_path}")

# Example usage
# add_number_labels_to_svg('files/keyboard_vectors/v2_keyboard_tidied.svg', 'files/keyboard_vectors/v3_keyboard_labeled.svg')