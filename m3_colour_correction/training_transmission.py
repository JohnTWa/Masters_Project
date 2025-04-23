# from _SETUP_ import set_directory
# set_directory()

# from common.reset import reset
# import common.keyboard_interface as keyboard
# import common.file_handling as fh

# # Packages
# import random
# import time
# import logging

# def random_colours(n_of_keys, seed=None):
    
#     grouped_colours = []
#     colours = []

#     # Set seed
#     if seed is not None:
#         random.seed(seed)

#     for _ in range(n_of_keys):

#         R = random.randint(0, 255)
#         G = random.randint(0, 255)
#         B = random.randint(0, 255)

#         grouped_colours.append((R, G, B))
#         colours.extend((R, G, B))

#     return grouped_colours, colours

# def transmit_random_colours_with_CLK(logger, data_IDs, target_database, transmission_length=20, CLK_IDs=[0], frequency=5, seed_multiplier=19450716112921):

#     logger.info(f'Function called')
#     reset(target_database)
#     logger.info(f'Reset target database')

#     T_bit = 1/frequency
#     iterations = int(round(transmission_length*frequency,0))
#     n_data_keys = len(data_IDs)
#     key_IDs = CLK_IDs + data_IDs
#     # CLK States:
#     ON = (255, 255, 255)
#     OFF = (0, 0, 0)

#     setup_items = keyboard.keyboard_setup()
#     logger.info(f'Connected to keyboard')

#     time.sleep(0.1)

#     keyboard.set_colour_timed(setup_items, key_IDs, (255,0,0), 4)
#     keyboard.set_colour_timed(setup_items, key_IDs, (0,0,0), 1)
    
#     for i in list(range(0, int(iterations/2))):
        
#         # CLK OFF
#         keyboard.set_colour_timed(setup_items, CLK_IDs, OFF, T_bit/2, 0)
#         grouped_colours, colours = random_colours(n_data_keys, seed=(i+1))
#         keyboard.set_colours_timed(setup_items, data_IDs, grouped_colours, T_bit/2, 0)
#         fh.write_to_csv_new_row(target_database, *colours)
#         logger.info(f'Random colours at OFF state set for iteration {i} of {iterations}')
                
#         # CLK ON
#         keyboard.set_colour_timed(setup_items, CLK_IDs, ON, T_bit/2, 0)
#         grouped_colours, colours = random_colours(n_data_keys, seed=(i+1)*seed_multiplier)
#         keyboard.set_colours_timed(setup_items, data_IDs, grouped_colours, T_bit/2, 0)
#         fh.write_to_csv_new_row(target_database, *colours)
#         logger.info(f'Random colours at OFF state set for iteration {i} of {iterations}')
    
#     # Switch CLK OFF
#     keyboard.set_colour_timed(setup_items, CLK_IDs, OFF, T_bit/2, 0)

#     # FINAL (UNIFORM WHITE)
#     keyboard.set_colour_timed(setup_items, data_IDs, ON, T_bit, 0)

#     # OFF
#     keyboard.set_colour(setup_items, data_IDs, OFF)

# # RUNNING:

# if __name__ == "__main__":

#     log_file_path = 'files/logs/Training_Data_Production.log'
#     target_database = 'files/spreadsheets/target_data.csv'
#     logging.basicConfig(
#         filename=log_file_path,
#         filemode='w',
#         format='%(asctime)s \t %(levelname)s \t %(message)s',
#         level=logging.INFO
#     )
#     logger = logging.getLogger(__name__)

#     key_IDs = fh.csv_to_list("files/spreadsheets/s1_key_IDs.csv")
#     key_IDs = fh.adjust_for_Corsair_logo(key_IDs)
#     CLK_IDs = [0]
#     data_IDs = key_IDs.copy()
#     data_IDs.remove(CLK_IDs[0])
#     n_data_keys = len(data_IDs)
#     print(n_data_keys) 

#     transmit_random_colours_with_CLK(logger, data_IDs, target_database)