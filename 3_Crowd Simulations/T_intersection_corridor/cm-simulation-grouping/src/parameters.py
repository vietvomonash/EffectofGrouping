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
            
            'targets'                            :[(35.0,25.0)],
           
            'start_areas'                         : [
                                                     (-70.0,10.0,-40.0,40.0),
                                                     (110.0,10.0,140.0,40.0), 
                                                    ],
             
            'walls'                               : [
                                                     (-1000.0,41.0,1000.0, 41.0), 
                                                     (-1000.0,9.0,20.0, 9.0),
                                                     (50.0,9.0,1000.0, 9.0),
                                                     (20.0,9.0,20.0,-1000.0),
                                                     (50.0,9.0,50.0,-1000.0),
                                                    ],
                                                         
            'monitor_point'                         : -50,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 2500,
            'drawing_height'                      : 1200,
            'pixel_factor'                        : 8,
        })
}