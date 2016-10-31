'''
Created on 28 Sep 2015

@author: quangv
'''

class RadiiGenerator(object):
    
    def __init__(self, parameters, group_num):
        self.parameters = parameters     
        self._reset_radii()
        self.total_population_num = group_num 
       
    def _reset_radii(self):
      
        self.radii_for_group = []
        self.max_radii = 0.0
    
    def _generate_radii(self):

        self.radii_for_group.clear()
        self.radii_for_group = [self.parameters['radius_mean']] * self.total_population_num
        self.max_radii = self.parameters['radius_mean']    
           
    def _get_radii_for_group(self):
        return self.radii_for_group
    
    def _set_radii_for_group(self,radii_group):
        self.radii_for_group = radii_group
                
    def _get_max_radii(self):
        return self.max_radii   
    
    def _set_max_radii(self,max_radii):
        self.max_radii = max_radii 
    
    def _get_total_population(self):
        return self.total_population_num
    
    def _set_total_population(self,total_num):
        self.total_population_num = total_num