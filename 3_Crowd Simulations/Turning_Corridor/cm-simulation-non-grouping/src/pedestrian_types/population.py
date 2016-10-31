'''
Created on 13 Feb 2015

@author: quangv
'''

from src.pedestrian_types.member import Member as member
import random as rd

class PopulationGenerator:
    
    def __init__(self, parameters,
                    in_group_a_strength, in_group_a_range,
                    in_group_r_strength, in_group_r_range,
                    out_group_a_strength, out_group_a_range, 
                    out_group_r_strength, out_group_r_range,
                    target_a_strength, target_a_range,group_num=[0,0]):
        
        self.parameters = parameters
        
        if len(group_num)==2:
            if group_num[0] != 0 and group_num[0] !=0:
                self.parameters['group_num'] = group_num
        
        self.total_group_num = len(self.parameters['group_num'])        
        self.group_generated_pedestrians = []
        
        for group_index in range(self.total_group_num):
            group_num = self.parameters['group_num'][group_index]
            
            group_dist = member(parameters)
                       
            if group_num >0:
                group_dist._generate_member_distribution(group_num,
                                                        in_group_a_strength, in_group_a_range,
                                                        in_group_r_strength, in_group_r_range,
                                                        out_group_a_strength, out_group_a_range, 
                                                        out_group_r_strength, out_group_r_range,
                                                        target_a_strength, target_a_range)
            
                """ add to groups"""
                self.group_generated_pedestrians.append(group_dist)
    
    def _generate_population(self,     
                             placement_radii_info,
                             placement_position_info, start_ped_id=0):
        
        self.generated_group_pedestrians = []
        self.generated_group_member_index = start_ped_id
        
        """ generate radii for all population based on total_group_num"""
        for i in range(self.total_group_num):
            radii_for_group = placement_radii_info[i]["radii_group"]
            position_group = placement_position_info[i]["position_group"] 

            group_num = self.parameters['group_num'][i]
            group_dist = self.group_generated_pedestrians[i]
            
            group_id = self.parameters['group_id'][i]
            
            if group_num > 0:
                pedestrians= self._create_pedestrian_by_distribution(group_id, group_dist, position_group, radii_for_group)
                if pedestrians is not None and len(pedestrians)>0:
                    for group_member in  pedestrians:                
                        self.generated_group_pedestrians.append(group_member)
     

    def _create_pedestrian_by_distribution(self, group_id, group_dist, designated_positions, radiis):

        pedestrians_in_same_group =[]
        
        in_group_a_strength = group_dist.get_in_group_a_strength()
        in_group_a_range = group_dist.get_in_group_a_range()
        in_group_r_strength = group_dist.get_in_group_r_strength()
        in_group_r_range = group_dist.get_in_group_r_range()
        
        out_group_a_strength = group_dist.get_out_group_a_strength()
        out_group_a_range =  group_dist.get_out_group_a_range()
        out_group_r_strength = group_dist.get_out_group_r_strength()
        out_group_r_range = group_dist.get_out_group_r_range()

        #target attraction
        target_a_strength = group_dist.get_target_a_strength()
        target_a_range =  group_dist.get_target_a_range()
              
        for i in range(len(designated_positions)):
      
            pedestrian_id = self.generated_group_member_index
            self.generated_group_member_index+=1
            
            pedestrians_in_same_group.append(dict(
                pedestrian_id = pedestrian_id,#
                group_id = group_id,#
                radius = radiis[i],#
                
                position = designated_positions[i]['position'],#
                
                in_group_a_strength = in_group_a_strength[i],#
                in_group_a_range = in_group_a_range[i],#
                in_group_r_strength = in_group_r_strength[i],#
                in_group_r_range = in_group_r_range[i],
                
                out_group_a_strength = out_group_a_strength[i],#
                out_group_a_range = out_group_a_range[i],
                out_group_r_strength = out_group_r_strength[i],
                out_group_r_range = out_group_r_range[i],
                
                #target point
                target = designated_positions[i]['target'],#
                target_a_strength = target_a_strength[i],
                target_a_range = target_a_range[i]))#
                   
        
        return pedestrians_in_same_group
    
    
    def _get_ids_group(self):
        
        ids_each_group = []
        for pedestrian in self.generated_group_pedestrians:
            ids_each_group.append(pedestrian['pedestrian_id'])

        return ids_each_group
    
    def _get_ped_id_coordination(self): #this only work if if nearby_in_group==1:
        
        ids_coordinate = []
        for pedestrian in self.generated_group_pedestrians:
            coord = (pedestrian['pedestrian_id'],pedestrian['position'][0],pedestrian['position'][1])
            ids_coordinate.append(coord)
                
        return ids_coordinate
    
    def _initialize_generated_group_pedestrians_population(self,ids_each_group):
        
        number_in_same_group = int(len(self.generated_group_pedestrians)/2)
        
        for pedestrian in self.generated_group_pedestrians:     
            group_list = []
            while (len(group_list))!=number_in_same_group:
                
                group_list = rd.sample(ids_each_group,number_in_same_group)
                #remove if it contain the same id of this pedestrian
                try:
                    group_list.remove(pedestrian['pedestrian_id'])
                except:
                    pass
                
            pedestrian['friend_zone'] = tuple(group_list)
            pedestrian['attractor_count'] = len(group_list)
        
        return self.generated_group_pedestrians

    def _initialize_generated_group_pedestrians_friend_zone(self, additional_ped_info):
    
        for pedestrian in self.generated_group_pedestrians:
            friend_zone = additional_ped_info[pedestrian['pedestrian_id']]
            group_list = []
            for item in friend_zone:
                group_list.append(int(item))
                
            pedestrian['friend_zone'] = tuple(group_list)#friend_zone
            pedestrian['attractor_count'] = len(group_list)            
        
        return self.generated_group_pedestrians
           
    #if len(ids_each_group)==0: #this is at the begining ofgame we should have another fuction    
    def _get_generated_group_pedestrians_population(self,ids_each_group): 
        
        #here we need to assign group mates for each pedestrian
        number_in_same_group = int(len(ids_each_group)/2)
        
        #another array to store additional ID for previous pedestrian
        additional_id_existed_ped = dict()
        for existed_ped in ids_each_group:
            additional_id_existed_ped[existed_ped] = [] #initialize the list for that
            
        for pedestrian in self.generated_group_pedestrians:     
            group_list = rd.sample(ids_each_group,number_in_same_group)
            pedestrian['friend_zone'] = tuple(group_list)
            pedestrian['attractor_count'] = len(group_list)
             
            #1/2 rest of the world will consider this guy to be attractor or not
            group_list_for_existed = rd.sample(ids_each_group,number_in_same_group)
            for existed_pedestrian_index in range(len(ids_each_group)):
                if ids_each_group[existed_pedestrian_index] in group_list_for_existed:
                    additional_id_existed_ped[ids_each_group[existed_pedestrian_index]].append(pedestrian['pedestrian_id'])

        return self.generated_group_pedestrians,additional_id_existed_ped
    