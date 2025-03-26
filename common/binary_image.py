from PIL import Image
import matplotlib.pyplot as plt

# Local Functions
from common.image_displaying import display_image

def image_to_binary(file_path):

    try:
        with open(file_path, 'rb') as file:
            image_bytes = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} does not exist.")
    
    # Convert each byte to an 8-bit binary string
    binary_list = [format(byte, '08b') for byte in image_bytes]
    
    return binary_list

def display_pgm_with_pillow(file_path):
    # Open the image using Pillow
    image = Image.open(file_path)
    
    # Convert the image to a NumPy array for display if needed
    plt.imshow(image, cmap='gray')
    plt.title(f"PGM Image: {file_path}")
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    display_pgm_with_pillow('files/images/PGM.pgm')
    display_image('files/images/PGM.pgm')