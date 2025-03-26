from _SETUP_ import set_directory
set_directory() 

import os
from common.image_displaying import display_image, produce_overlaid_image, reconstruct_svg, display_colours
from common.reset import reset
from vp_2_point_selection import point_selection
from vp_3_image_warping import image_warping
from vp_4_vector_fitting import vector_fitting
from vp_5_key_identification import save_coordinates_to_csv
# from vp_6_colour_averaging import colour_averaging

# Define file paths

input_image_path = 'files/frames/frame_268.png'
corners_csv_path = 'files/s1_corner_coordinates.csv'
warped_image_path = 'files/i2_warped_image.png'
mesh_vector_path = 'files/keyboard_vectors/v1_keyboard.svg'
tidied_vector_path = 'files/keyboard_vectors/v2_keyboard_tidied.svg'
overlaid_image_path = 'files/i3_overlaid_image.png'
fitted_vector_path = 'files/keyboard_vectors/v4_fitted_mesh.svg'
coordinates_csv_path = 'files/s2_key_coordinates.csv'
reconstructed_vector_path = 'files/keyboard_vectors/v5_reconstructed_mesh.svg'
reconstructed_overlaid_path = 'files/i4_reconstructed_overlaid.jpg'
rgb_csv_path = 'files/s3_rgb_averages.csv'
coloured_vector_path = 'files/keyboard_vectors/v6_coloured_mesh.svg'

# Run the overlay function

reset(rgb_csv_path)
# tidy_keyboard_vector_reorder_rows(mesh_vector_path, tidied_vector_path)
# point_selection(input_image_path, corners_csv_path)
image_warping(input_image_path, corners_csv_path, warped_image_path)
display_image(warped_image_path)
# vector_fitting(mesh_vector_path, warped_image_path, fitted_vector_path)
# produce_overlaid_image(fitted_vector_path, warped_image_path, overlaid_image_path)
# display_image(overlaid_image_path)
# save_coordinates_to_csv(fitted_vector_path, coordinates_csv_path)
# reconstruct_svg(coordinates_csv_path, reconstructed_vector_path)
# produce_overlaid_image(reconstructed_vector_path, warped_image_path, reconstructed_overlaid_path)
# display_image(reconstructed_overlaid_path)
# colour_averaging(warped_image_path, coordinates_csv_path, rgb_csv_path)
# display_colours(reconstructed_vector_path, rgb_csv_path, coloured_vector_path, 1)
# display_image(coloured_vector_path)