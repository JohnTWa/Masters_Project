import numpy as np
from PIL import Image

def filter_png_by_numpy(png_file_path, numpy_file_path):
    """
    Filters a PNG image so that only the pixels specified by the numpy mask are visible.
    All other pixels are set to fully transparent.

    Parameters:
    - png_file_path (str): Path to the input PNG image.
    - numpy_file_path (str): Path to the .npy file containing the mask.
      The mask is expected to be an RGBA array (with shape (height, width, 4))
      where pixels to be retained have a non-zero alpha value.

    Returns:
    - filtered_img (PIL.Image.Image): The filtered image in RGBA mode.
    """
    # Open the input image and ensure it is in RGBA mode
    img = Image.open(png_file_path).convert("RGBA")
    img_arr = np.array(img)

    # Load the mask array from the numpy file
    mask_arr = np.load(numpy_file_path)

    # Verify that the mask dimensions match the input image dimensions
    if mask_arr.shape[:2] != img_arr.shape[:2]:
        raise ValueError("The dimensions of the mask do not match the dimensions of the input image.")

    # Create a boolean mask: True where the mask pixel's alpha channel is non-zero
    selected_pixels = mask_arr[..., 3] > 0

    # Prepare an output array initialized to fully transparent pixels
    filtered_arr = np.zeros_like(img_arr)

    # Copy over the pixels from the original image that are marked in the mask
    filtered_arr[selected_pixels] = img_arr[selected_pixels]

    # Convert the filtered numpy array back to a PIL Image
    filtered_img = Image.fromarray(filtered_arr, "RGBA")
    return filtered_img

def produce_png_from_numpy(numpy_file_path, color=(0, 0, 0, 255)):
    """
    Produces a backgroundless PNG image from a numpy file, with the mask shown in the specified color.

    Parameters:
    - numpy_file_path (str): Path to the .npy file containing the mask.
      The mask is expected to be an RGBA array (with shape (height, width, 4))
      where pixels to be retained have a non-zero alpha value.
    - color (tuple): The desired color for the mask. It should be a tuple of four integers (R, G, B, A).
    
    Returns:
    - img (PIL.Image.Image): The produced image in RGBA mode.
    """
    # Load the mask array from the numpy file
    mask_arr = np.load(numpy_file_path)
    
    # Ensure the mask is in proper RGBA format
    if mask_arr.shape[2] != 4:
        raise ValueError("The numpy array must have 4 channels (RGBA).")
    
    # Create an empty array for the output image with fully transparent pixels
    img_arr = np.zeros(mask_arr.shape, dtype=np.uint8)
    
    # Create a boolean mask where the mask pixel's alpha channel is non-zero
    selected_pixels = mask_arr[..., 3] > 0
    
    # Apply the specified color to the selected pixels
    img_arr[selected_pixels] = color

    # Convert the numpy array to a PIL Image
    img = Image.fromarray(img_arr, "RGBA")
    return img

# Example usage:
if __name__ == "__main__":
    input_png_path = "files/warped_frames/warped_frame_0.png"      # Replace with your PNG file path
    mask_numpy_path = "files/a1_LED_mask.npy"          # Replace with your .npy mask file path
    output_image_path = "files/filtered_image.png"  # Where to save the filtered image

    result_image = filter_png_by_numpy(input_png_path, mask_numpy_path)
    result_image.save(output_image_path, "PNG")
    print(f"Filtered image saved to: {output_image_path}")

    LED_mask_image_path = "files/LED_mask.png"
    LED_mask_image = produce_png_from_numpy(mask_numpy_path)
    LED_mask_image.save(LED_mask_image_path, "PNG")



