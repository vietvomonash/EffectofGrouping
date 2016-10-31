'''
Created on 1 Feb 2016

@author: quangv
'''
from src import constants 
import os, json
from src.utility.influential import Influential_Member as influential_member
from src.utility.influential import Influential_Member_Encoder
from src.utility.influential import Influential_Member_Decoder

class ObservationPlots:

    def __init__(self, parameters):
        
        self.parameters = parameters
                    
        self.influential_matrix_split_area = dict()
        self.influential_matrix_merge_area = dict()
        
        self.turning_angle_split_area = []
        self.turning_angle_merge_area = []
        
        self.effectiveness_split_area = []
        self.effectiveness_merge_area = []               
                                                         
    def _add_new_sample(self, turning_angle_split_area,turning_angle_merge_area,
                            total_effective_split,total_effective_merge,
                            influential_matrix_split_area,influential_matrix_merge_area):
        
        if len(turning_angle_split_area)>0:
            for item in turning_angle_split_area:
                self.turning_angle_split_area.append(item)

        if len(turning_angle_merge_area)>0:
            for item in turning_angle_merge_area:
                self.turning_angle_merge_area.append(item)
                        
        if total_effective_split !=0.0:
            self.effectiveness_split_area.append(total_effective_split)

        if total_effective_merge !=0.0:
            self.effectiveness_merge_area.append(total_effective_merge)
                
        for key in influential_matrix_split_area:
            if key in self.influential_matrix_split_area:
                self.influential_matrix_split_area[key].append(influential_matrix_split_area[key])
            else:
                self.influential_matrix_split_area[key] = [influential_matrix_split_area[key]]
                
        for key in influential_matrix_merge_area:
            if key in self.influential_matrix_merge_area:
                self.influential_matrix_merge_area[key].append(influential_matrix_merge_area[key])
            else:
                self.influential_matrix_merge_area[key] = [influential_matrix_merge_area[key]]
                                
 

    def reset_sample(self):
        
        self.influential_matrix_split_area = dict()
        self.influential_matrix_merge_area = dict()
        
        self.turning_angle_split_area = []
        self.turning_angle_merge_area = []
        
        self.effectiveness_split_area = []
        self.effectiveness_merge_area = []  
        
    def _dump_influential_matrix(self,context_index):
       
        influential_obj = influential_member(self.influential_matrix_split_area)              
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        frame_filename = "%s" % (str(disp_level) + "_" + str(context_index))
         
        log_file = open( "%s_split.json" % os.path.join(constants.influential_context_dir, frame_filename), "w")
        json_obj = json.dumps(influential_obj, cls=Influential_Member_Encoder)
        log_file.write(json_obj)
        log_file.close()
        
        influential_obj = influential_member(self.influential_matrix_merge_area)              
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        frame_filename = "%s" % (str(disp_level) + "_" + str(context_index))
         
        log_file = open( "%s_merge.json" % os.path.join(constants.influential_context_dir, frame_filename), "w")
        json_obj = json.dumps(influential_obj, cls=Influential_Member_Encoder)
        log_file.write(json_obj)
        log_file.close()
            
    def _get_turning_angle_split_area(self):
        return self.turning_angle_split_area
    
    def _get_turning_angle_merge_area(self):
        return self.turning_angle_merge_area
    
    def _get_effectiveness_split_area(self):
        return self.effectiveness_split_area
    
    def _get_effectiveness_merge_area(self):
        return self.effectiveness_merge_area
            