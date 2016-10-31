'''
Created on 29 Sep 2015

@author: quangv
'''
from src.utility.placement import PlacementGenerator 
from src.utility.radii import RadiiGenerator 
import json
import math, random
from src import constants

class ContextGenerator(object):
    
    def __init__(self, parameters, placement_num):
        
        self.parameters = parameters
        self.radii_generators = []
        self.placement_generators = []
        self.placement_num = placement_num
        self.total_population_num = 0
        
        grid_cell_size = self.parameters['radius_mean'] *2+0.05 #multiple 2 because there needs diameter             
        for group in self.parameters['group_num']:
            self.total_population_num += group
        
        grid = self._generate_placement_area(self.parameters, self.parameters['start_areas'], grid_cell_size)
                
        if self.total_population_num > len(grid):
            return

        i = 0
        while i < placement_num: 
             
            #we perform random for each placement simulation time
            cells = random.sample(grid, min(self.total_population_num,len(grid))) 
             
            for group in self.parameters['group_num']:
                num = group
                  
                radii_generator = RadiiGenerator(self.parameters,num)
        
                radii_generator._generate_radii()
            
                position_generator = PlacementGenerator(self.parameters,num)
                
                group_cell = random.sample(cells, num)
                cells = constants.remove_subset(cells,group_cell)
                
                position_generator._generate_placements(group_cell,grid_cell_size,radii_generator._get_radii_for_group())
        
                self.radii_generators.append(dict(
                                            radii_group = radii_generator._get_radii_for_group(),
                                            max_radii = radii_generator._get_max_radii()))
            
                self.placement_generators.append(dict(        
                                            position_group = position_generator._get_placements_for_group()))

            i+=1
    
    def _generate_placement_area(self,parameters, start_areas,cell_size):
        grid = list()
        for i in range(len(start_areas)):
            (x1,y1,x2,y2) = start_areas[i]
            t =  self.parameters['targets'][i]
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
    
    def _set_radii_generators(self,radii_generators):
        self.radii_generators = radii_generators
    
    def _get_placement_generators(self):
        return self.placement_generators
        
    def _set_placement_generators(self, placement_generators):
        self.placement_generators = placement_generators
           
    def _set_placement_num(self,placement_num):
        self.placement_num = placement_num
        
    def _get_placement_num(self):
        return self.placement_num
   
           
class ContextLog_Encoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, ContextGenerator):
            return super(ContextLog_Encoder, self).default(obj)
        return obj.__dict__

class ContextLog_Decoder(json.JSONDecoder):
    def decode(self,json_string):
     
        default_obj = super(ContextLog_Decoder,self).decode(json_string)
        
        parameters = default_obj['parameters']
        placement_num = default_obj['placement_num']
        
        radii_generators = []
        placement_generators = []
        
        str_radii_generators = default_obj['radii_generators']       
        for radius in str_radii_generators:
            radii_generators.append(dict(radii_group = radius['radii_group'],
                                         max_radii = radius['max_radii']))
                                       
        str_placement_generators = default_obj['placement_generators']    
        for placement_generator in str_placement_generators:
            placement_generators.append(dict(position_group = placement_generator['position_group']))

        
        context_generator = ContextGenerator(parameters,placement_num)
        
        context_generator._set_radii_generators(radii_generators)
        context_generator._set_placement_generators(placement_generators)
        
        return context_generator