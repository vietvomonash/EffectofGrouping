'''
Created on 1 Feb 2016

@author: quangv
'''
import numpy as np
from src import constants 
import os, json
import csv
from src.utility.influential import Influential_Member as influential_member
from src.utility.influential import Influential_Member_Encoder
from src.utility.influential import Influential_Member_Decoder

class ObservationPlots:

    def __init__(self, parameters):
        
        self.parameters = parameters
        self.total_group_num = 0
        
        for group_num in self.parameters['group_num']:
            self.total_group_num += group_num
        
        self.time = []
        #self.average_velocity_x = []        
        #self.average_velocity_x_position =  [[] for j in range(601)] 
        self.total_velocities_trajectories = [[] for j in range(self.total_group_num)] #since we have at the beginning
        
        self.influential_member_matrix = dict()
                

    def _add_new_sample(self, t, velocity_trajectories,influential_matrix):
        
        self.time.append(t)
        
        #perform add velocity_trajectories
        range_trajectory_len = min (len(velocity_trajectories),len(self.total_velocities_trajectories))
        for pedestrian_index in range(range_trajectory_len):
                self.total_velocities_trajectories[pedestrian_index].append(velocity_trajectories[pedestrian_index])
        
        
        #add for new spawn  pedestrians
        additional_size = len(velocity_trajectories)-len(self.total_velocities_trajectories)
        if additional_size > 0:
            new_array = [[] for j in range(additional_size)]
            for pedestrian_index in range(additional_size):
                new_array[pedestrian_index].append(velocity_trajectories[pedestrian_index+len(self.total_velocities_trajectories)]) 
            
            for item in new_array:
                self.total_velocities_trajectories.append(item)        

    
    
        for key in influential_matrix:
            if key in self.influential_member_matrix:
                self.influential_member_matrix[key].append(influential_matrix[key])
            else:
                self.influential_member_matrix[key] = [influential_matrix[key]]
                
                
    def get_velocity_by_x_position(self):

        x_position_measurement = [ scale_meter for scale_meter in range(0, 601)]
        
        #we first compute average velocity of pedestrian at position        
        avg_velocity_positions_crowd = [[] for x_position in range(len(x_position_measurement))] 
                
        for pedestrian_index in range(len(self.total_velocities_trajectories)):
            trajectory = self.total_velocities_trajectories[pedestrian_index]
            avg_velocity_positions, flags = self.parse_trajectory_pedestrian(trajectory, x_position_measurement)
            # add into the final avg_velocity_positions_crowd
            for x_position_index in range(len(avg_velocity_positions)):
                if avg_velocity_positions[x_position_index] != 0 or (avg_velocity_positions[x_position_index] == 0 and flags[x_position_index] == 1):
                    avg_velocity_positions_crowd[x_position_index].append(avg_velocity_positions[x_position_index])

                            
        #we then average at this simulation
        avg_velocity = [0] * len(x_position_measurement)
        for x_position_index in range(len(x_position_measurement)):
            if len(avg_velocity_positions_crowd[x_position_index]) > 0:
                avg_velocity[x_position_index] = np.mean(avg_velocity_positions_crowd[x_position_index])

        return avg_velocity

    def reset_sample(self):
        self.time = []

        #self.average_velocity_x = []        
        #self.average_velocity_x_position =  [[] for j in range(601)] 
        self.total_velocities_trajectories = [[] for j in range(self.total_group_num)] #since we have 100 pedestrians as the beginning 
                
    
    def parse_trajectory_pedestrian(self,trajectory, x_position_measurement):
    
        velocities_at_x_positions = [[] for x_position in range(len(x_position_measurement))]
        
        for data_point_index in range(len(trajectory)):
            
            if trajectory[data_point_index][0] >= 0.0 and trajectory[data_point_index][0] <= 600:  # we only measure from the meter 0-600
                velocities_at_x_positions[int(trajectory[data_point_index][0])].append(trajectory[data_point_index][2])
        
        avg_velocity_positions = [0] * len(x_position_measurement)
        # this flag is to check whether velocity equal 0 (pedestrians actual stops) or this pedestrian has not reached at this position
        flags = [0] * len(x_position_measurement)
        for position_index in range(len(velocities_at_x_positions)):
            if len(velocities_at_x_positions[position_index]) > 0:
                avg_velocity_positions[position_index] = np.mean(velocities_at_x_positions[position_index]) 
                if avg_velocity_positions[position_index] == 0: 
                    flags[position_index] = 1
        
        return avg_velocity_positions, flags
 
    def dump_velocity_log(self, seperation_c_value , current_simulation_run):
        
        #dump for velocity-x position over time
        '''velocity_overtime_file = open( "%s.csv" % os.path.join(constants.log_velocity_over_time_dir, seperation_c_value, current_simulation_run), "w", newline='')
        writer1 = csv.writer(velocity_overtime_file,delimiter=',')
        writer1.writerow((self.average_velocity_x))
        velocity_overtime_file.close()
        
        
        #dump for velocity-x over x-distribution, remember to add index
        velocity_over_position_file = open( "%s.csv" % os.path.join(constants.log_velocity_x_position_dir, seperation_c_value, current_simulation_run), "w", newline='')
        writer2 = csv.writer(velocity_over_position_file,delimiter=',')
             
        for index in range(len(self.average_velocity_x_position)):
            writer2.writerow((index, self.average_velocity_x_position[index]))
        
        velocity_over_position_file.close()'''
        
        #dump trajectories into file
        trajectories_file = open( "%s.csv" % os.path.join(constants.log_trajectories_dir, seperation_c_value, current_simulation_run), "w", newline='')
        writer3 = csv.writer(trajectories_file,delimiter=',') 
        for pedestrian_index in range(len(self.total_velocities_trajectories)):
            writer3.writerow((pedestrian_index, self.total_velocities_trajectories[pedestrian_index]))
        

        trajectories_file.close()
    
    
    def _dump_influential_matrix(self,context_index):
       
        influential_obj = influential_member(self.influential_member_matrix)              
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        frame_filename = "%s" % (str(disp_level) + "_" + str(context_index))
         
        log_file = open( "%s.json" % os.path.join(constants.influential_context_dir, frame_filename), "w")
        json_obj = json.dumps(influential_obj, cls=Influential_Member_Encoder)
        log_file.write(json_obj)
        log_file.close()
        
             
    '''def _add_sample(self,  t,  avg_velocity_x, velocity_x_position_scale, velocity_trajectories): 
      
        self.time.append(t)
    
        #perform add average velocity x direction
        self.average_velocity_x.append(avg_velocity_x)        
       
        #perform for velocity_x _meter
        for scale_meter in range(len(velocity_x_position_scale)):
            if len(velocity_x_position_scale[scale_meter]) > 0:
                for velocity in velocity_x_position_scale[scale_meter]:
                    self.average_velocity_x_position[scale_meter].append(velocity)
        

        #perform add velocity_trajectories
        range_trajectory_len = min (len(velocity_trajectories),len(self.total_velocities_trajectories))
        for pedestrian_index in range(range_trajectory_len):
                self.total_velocities_trajectories[pedestrian_index].append(velocity_trajectories[pedestrian_index])
        
        
        #add for new spawn  pedestrians
        additional_size = len(velocity_trajectories)-len(self.total_velocities_trajectories)
        if additional_size > 0:
            new_array = [[] for j in range(additional_size)]
            for pedestrian_index in range(additional_size):
                new_array[pedestrian_index].append(velocity_trajectories[pedestrian_index+len(self.total_velocities_trajectories)]) 
            
            for item in new_array:
                self.total_velocities_trajectories.append(item)    
        
    def get_velocity_x(self):
        return self.average_velocity_x '''                   