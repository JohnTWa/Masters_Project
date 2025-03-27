from _SETUP_ import set_directory
set_directory()

import os
import joblib
from common.image_displaying import display_image, produce_overlaid_image, reconstruct_svg, display_colours
from common.reset import reset
from vp_0_vector_tidying import tidy_keyboard_vector_reorder_rows
from vp_1_video_frame_splitting import video_frame_splitting
from vp_2_point_selection import point_selection
from vp_3_image_warping import image_warping
from vp_4_vector_fitting import vector_fitting
from vp_5_key_identification import save_coordinates_to_csv
from vp_6_LED_identification import LED_identification
from vp_7_LED_colour_averaging import LED_colour_averaging
from vp_8_timestamping import frame_timestamping
from vp_9_colour_correction import normalise_rgb, predict_rgb_values

# Define folder paths

frames_folder = 'files/frames'
warped_frames_folder = 'files/warped_frames'
images_folder = 'files/images'
keyboard_vectors_folder = 'files/keyboard_vectors'
coloured_keyboards_folder = 'files/coloured_keyboards'
spreadsheets_folder = 'files/spreadsheets'

## Define file paths

video_path = 'files/ASK Synchronous Image Transmission.mp4'
input_image_path = frames_folder + '/frame_0.png'
corners_csv_path = spreadsheets_folder + '/s2_corner_coordinates.csv'
warped_image_path = warped_frames_folder + '/warped_frame_0.png'
keyboard_vector_path = keyboard_vectors_folder + '/v1_keyboard_with_CLK.svg'
tidied_vector_path = keyboard_vectors_folder + '/v2_keyboard_tidied.svg'
overlaid_image_path = images_folder + '/i3_overlaid_image.png'
fitted_vector_path = keyboard_vectors_folder + '/v4_fitted_mesh.svg'
coordinates_csv_path = spreadsheets_folder + '/s3_key_coordinates.csv'
reconstructed_vector_path = keyboard_vectors_folder + '/v5_reconstructed_mesh.svg'
reconstructed_overlaid_path = images_folder + '/i4_reconstructed_overlaid.jpg'
LED_mask_numpy_path = 'files/a1_LED_mask.npy'
LED_mask_image_path = images_folder + '/i5_LED_mask.png'
LED_mask_overlaid_path = images_folder + '/i6_LED_overlay.png'
rgb_csv_path = spreadsheets_folder + '/s4_rgb_averages.csv'
normalised_rgb_csv_path = spreadsheets_folder + '/s5_rgb_normalised.csv'
model_filepath = 'files/p1_regression_model.pkl'
corrected_rgb_csv_path = spreadsheets_folder + '/s6_rgb_corrected.csv'
coloured_vector_path = keyboard_vectors_folder + '/coloured_keyboards/coloured_keyboard_0.svg'
timestamps_csv_path = spreadsheets_folder + '/s7_frame_timestamps.csv'

## Settings ##

# first_frame = 248
# first_frame_timestamp = '2025-02-03-16-24-52-767'

## Reset Files as Required ##

reset(frames_folder)
reset(warped_frames_folder)
reset('files/keyboard_vectors/coloured_keyboards', rgb_csv_path)

## Run the Process for Initial Frame

video_frame_splitting(video_path, frames_folder)
point_selection(input_image_path, corners_csv_path)
image_warping(input_image_path, corners_csv_path, warped_image_path)
#display_image(warped_image_path)
vector_fitting(keyboard_vector_path, warped_image_path, fitted_vector_path)
# produce_overlaid_image(fitted_vector_path, warped_image_path, overlaid_image_path)
# display_image(overlaid_image_path)
save_coordinates_to_csv(fitted_vector_path, coordinates_csv_path)
reconstruct_svg(coordinates_csv_path, reconstructed_vector_path)
produce_overlaid_image(reconstructed_vector_path, warped_image_path, reconstructed_overlaid_path)
display_image(reconstructed_overlaid_path)
LED_identification(warped_image_path, coordinates_csv_path, LED_mask_image_path, LED_mask_numpy_path)
produce_overlaid_image(None, warped_image_path, LED_mask_overlaid_path, LED_mask_image_path)
display_image(LED_mask_overlaid_path)

## Repeat for all frames 

frame_number = 0
while os.path.exists(input_image_path):

    image_warping(input_image_path, corners_csv_path, warped_image_path)
    LED_colour_averaging(warped_image_path, coordinates_csv_path, LED_mask_numpy_path, rgb_csv_path)

    frame_number += 1

    input_image_path = f'files/frames/frame_{frame_number}.png'
    warped_image_path = f'files/warped_frames/warped_frame_{frame_number}.png'

# frame_timestamping(video_path, first_frame, first_frame_timestamp, timestamps_csv_path)
normalise_rgb(rgb_csv_path, normalised_rgb_csv_path)
predict_rgb_values(rgb_csv_path, corrected_rgb_csv_path, model=joblib.load(model_filepath))