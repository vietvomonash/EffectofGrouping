'''
Created on 16 Feb 2015

@author: quangv
'''
import numpy as np
import random

timestep              = 0.02 #time step to calculate new position and velocity
total_monitoring_duration_uni_direction = 100#50# total time for our simulation in unique directional flow

observation_dir  = "../observation/" # folder for storing observation plotting figure
analysis_dir = "../analysis/" #folder to store analysis plot
context_dir = "../context/" #folder to store context
adaptive_dir = "../adaptive/" #folder to store adaptive context
influential_context_dir = "../influential/"
log_velocity_over_time_dir = "../log_velocity/velocity_over_time/"
log_velocity_x_position_dir = "../log_velocity/velocity_x_position/"
log_trajectories_dir = "../log_velocity/trajectories/"

image_dir = "../image/" #folder to store image
framecontext_dir = "../frame/"

framerate_limit       = int(round(1.0/timestep)) # frame rate per second to draw and update canvas = 5
plot_sample_frequency = 1
frame_store_sample_frequency = 20 #for each 20 seconds we store one frame; frame rate to dump frame log; 1000 stored frame = 20 seconds since 20/timestep = 1000
spawn_pedestrian_frequency = 2
spawn_rate = 4 #pedestrians



tracked_pedestrian_id = -1

def remove_subset(original_cells, removed_cells):
    #only remove one time in orginal_cess from items in removed_cells
    # since it may be floored before
    removed_items = []
    index=0
    while index<len(original_cells):
        if original_cells[index] in removed_cells and original_cells[index] not in removed_items:
            removed_items.append(original_cells[index])
            original_cells.remove(original_cells[index])
            
        else:
            index+=1;

    return original_cells 
  
def myround(a, decimals=1):
    return np.around(a-10**(-(decimals+5)), decimals=decimals)
  
def _filter_samples_by_mean(array, num):
        filtered_array =[item for item in array if item>0]
        if len(filtered_array) < num:
            return filtered_array
        else:
            return random.sample(filtered_array, num)

def _generate_log_title(group_id_list):

    c_d_log = []
    for group_index in range(len(group_id_list)):
            group_id = group_id_list[group_index]
            c_d_log.append("cohesion_degree" + str(group_id))

    log_title = ["SimulationId"] + c_d_log
    return log_title
        