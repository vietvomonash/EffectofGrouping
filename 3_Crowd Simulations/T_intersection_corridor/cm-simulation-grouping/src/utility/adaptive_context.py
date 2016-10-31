'''
Created on 9 May 2016

@author: quangv
'''
from src.utility.placement import PlacementGenerator 
from src.utility.radii import RadiiGenerator 
import json, math
import random
from math import hypot
from src import constants

class AdaptiveContextGenerator(object):
    
    def __init__(self, parameters):

        self.parameters = parameters
        self.radii_generators = []
        self.placement_generators = []
        self.total_population_num = 0
        
    def _generateContext(self,current_pedestrian_position,group_num, start_area):
        
        self.total_population_num = 0
        for num in group_num:
            self.total_population_num+=num
            
        
        radii = self.parameters['radius_mean'] *2+0.05
        grid_cell_size = radii #multiple 2 because there needs diameter             
        #grid = self._generate_placement_area(self.parameters['start_areas'], grid_cell_size)
        grid = self._generate_placement_area(start_area, grid_cell_size)
                
        cells = []
        while len(cells) != self.total_population_num: 
            cells = random.sample(grid, self.total_population_num) 
            
            #check overlap
            index_overlapped = []
            for index_cell in range(len(cells)):
                current_cell = cells[index_cell]  
                for pedestrian_position in current_pedestrian_position:
                    if hypot(current_cell[0] -pedestrian_position[0], current_cell[1] - pedestrian_position[1]) < radii*2:
                        index_overlapped.append(index_cell)
        
            #remove overlap                    
            index_overlapped = list(set(index_overlapped))
            for value in index_overlapped:
                while value in cells: cells.remove(value)
        
        for group in group_num:
            num = group
                  
            radii_generator = RadiiGenerator(self.parameters,num)
            radii_generator._generate_radii()
            group_cell = random.sample(cells, num)
            cells = constants.remove_subset(cells,group_cell)
                                    
            position_generator = PlacementGenerator(self.parameters,num)                
            position_generator._generate_placements(group_cell,grid_cell_size,radii_generator._get_radii_for_group())
        
            self.radii_generators.append(dict(
                                            radii_group = radii_generator._get_radii_for_group(),
                                            max_radii = radii_generator._get_max_radii()))
                
            self.placement_generators.append(dict(        
                                            position_group = position_generator._get_placements_for_group()))
                        
    def _generate_placement_area(self, start_areas,cell_size):
        grid = list()
        (x1,y1,x2,y2) = start_areas
        t =  self.parameters['targets'][0]
        x_range = x2-x1
        y_range = y2-y1
        x_offset = (x_range % cell_size)/2
        y_offset = (y_range % cell_size)/2
        cells_x = int(math.floor(x_range / cell_size))
        cells_y = int(math.floor(y_range / cell_size))
            
        for i in range(cells_x):
            for j in range(cells_y):
                grid.append((i * cell_size + x_offset + x1, 
                    j * cell_size + y_offset + y1,t))
        return grid
            
            
    def _get_radii_generators(self):
        return self.radii_generators
    
    def _get_placement_generators(self):
        return self.placement_generators  
    
    def _set_radii_generators(self,radii_generators):
        self.radii_generators = radii_generators
    
    def _set_placement_generators(self, placement_generators):
        self.placement_generators = placement_generators 
        
class AdaptiveContextLog_Encoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, AdaptiveContextGenerator):
            return super(AdaptiveContextLog_Encoder, self).default(obj)
        return obj.__dict__

class AdaptiveContextLog_Decoder(json.JSONDecoder):
    def decode(self,json_string):
     
        default_obj = super(AdaptiveContextLog_Decoder,self).decode(json_string)
        
        parameters = default_obj['parameters']
        
        radii_generators = []
        placement_generators = []
        
        str_radii_generators = default_obj['radii_generators']       
        for radius in str_radii_generators:
            radii_generators.append(dict(radii_group = radius['radii_group'],
                                         max_radii = radius['max_radii']))
                                       
        str_placement_generators = default_obj['placement_generators']    
        for placement_generator in str_placement_generators:
            placement_generators.append(dict(position_group = placement_generator['position_group']))

        
        context_generator = AdaptiveContextGenerator(parameters)
        context_generator._set_radii_generators(radii_generators)
        context_generator._set_placement_generators(placement_generators)
        
        return context_generator                     