'''
Created on 28 Sep 2015

@author: quangv
'''
import random

class PlacementGenerator(object):
    
    def __init__(self, parameters, group_num):
        self.parameters = parameters
     
        self._reset_placements()
        
        self.total_population_num = group_num
             
    def _reset_placements(self):
        
        self.max_radius = 0
        self.placements_for_group = []

    def _generate_placements(self, cells, grid_cell_size, radii_group):     
     
        if self.total_population_num > 0:
            cells_for_group = random.sample(cells, self.total_population_num)
            self.placements_for_group= self._create_placement_for_pedestrian_type(cells_for_group, radii_group, grid_cell_size) 
              
    def _create_placement_for_pedestrian_type(self, designated_cells, radii, grid_cell_size):
        
        pedestrians_in_same_type =[]
        
        for i in range(len(designated_cells)):
            radius = radii[i]
            cell = designated_cells[i]
            free_space_x = grid_cell_size - radius*2
            free_space_y = grid_cell_size - radius*2
            x_coord = random.random() * free_space_x + cell[0] + radius
            y_coord = random.random() * free_space_y + cell[1] + radius
            position = (x_coord, y_coord)
            target = cell[2]
            pedestrians_in_same_type.append(dict(
                position = position,
                target = target))
                    
        return pedestrians_in_same_type

    def _get_max_radius(self):
        return self.max_radius
    
    def _set_max_radius(self,radius):
        self.max_radius = radius
        
    def _get_placements_for_group(self):
        return self.placements_for_group      
    
    def _set_placements_for_group(self,placements):
        self.placements_for_group = placements   
    
    def _get_total_population(self):
        return self.total_population_num
    
    def _set_total_population(self,total_num):
        self.total_population_num = total_num