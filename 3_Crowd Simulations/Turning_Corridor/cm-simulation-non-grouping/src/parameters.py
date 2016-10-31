'''
Created on 16 Feb 2015

@author: quangv
'''
from pygame_drawing.scenario import Scenario

scenarios = {             
        'narrowcorridor': Scenario({
            'name'                    : 'narrow-corridor',          

            'group'                   : 2,
            
            'group_num'               : [10,10],
            
            'group_id'                : [0,1], #it should start from 0
            
            'radius_mean'             : 0.3,
            
            'targets'                            :[(16.0,-39.0)],
           
            'start_areas'                         : [
                                                     (-10.0,36.0,20.0,72.0), #only adjust width, do not adjust length
                                                    ],
             
            'walls'                               : [
                                                     (-11.0,1000.0,-11.0, -54.0),  #only adjust width, do not adjust length
                                                     (21.0,1000.0,21.0, -24.0),
                                                     (-11.0,-54.0,1000.0, -54.0),#9.1, 9.0
                                                     (21.0,-24.0,1000.0,-24.0),
                                                    ],
                                                         
            'monitor_point'                         : 120,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 2500,
            'drawing_height'                      : 1200,
            'pixel_factor'                        : 8,
        })
}