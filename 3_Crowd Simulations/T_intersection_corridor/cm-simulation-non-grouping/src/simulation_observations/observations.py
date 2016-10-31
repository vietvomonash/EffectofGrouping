'''
Created on 1 Feb 2016

@author: quangv
'''
import os, json
from src.utility.influential import Influential_Member as influential_member
from src.utility.influential import Influential_Member_Encoder
from src.utility.influential import Influential_Member_Decoder
from src import constants 

class ObservationPlots:

    def __init__(self, parameters):
        
        self.parameters = parameters

        
        self.turning_angles = []
        self.total_effect = []
        
        self.influential_member_matrix = dict()
        

    def _add_new_sample(self,turning_angle,total_effective,influential_matrix):
        
        if len(turning_angle)>0:
            for item in turning_angle:
                self.turning_angles.append(item)
        
        if total_effective !=0.0:
            self.total_effect.append(total_effective)
            
        
        for key in influential_matrix:
            if key in self.influential_member_matrix:
                self.influential_member_matrix[key].append(influential_matrix[key])
            else:
                self.influential_member_matrix[key] = [influential_matrix[key]]
                
    def _dump_influential_matrix(self,context_index):
       
        influential_obj = influential_member(self.influential_member_matrix)              
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        frame_filename = "%s" % (str(disp_level) + "_" + str(context_index))
         
        log_file = open( "%s.json" % os.path.join(constants.influential_context_dir, frame_filename), "w")
        json_obj = json.dumps(influential_obj, cls=Influential_Member_Encoder)
        log_file.write(json_obj)
        log_file.close()
        
                       
    def reset_sample(self):

        self.turning_angles = []
        self.total_effect = []    
        self.influential_member_matrix = dict()
                      
    def get_turning_angles(self):
        return self.turning_angles
            
    def get_effective_evacuation(self):
        return self.total_effect                  