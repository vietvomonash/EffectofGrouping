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
            
            'targets'                                :[(10000.0,0.0)],

                      
            #note that -30 = 0            
            ## d1 = 30
            'start_areas'                         : [
                                                     (-70,-24,-30.0, 24.0), #only adjust width, do not adjust length
                                                    ],
             
            'walls'                               : [
                                                     (-500.0,-25,500.0, -25.0),  #only adjust width, do not adjust length
                                                     (-500.0,25,500.0, 25.0),
                                                     (60.0,2,100.0, 2.0),#9.1, 9.0
                                                     (60.0,-2,100.0,-2.0),
                                                     (60.0, -2.0, 60.0, 2.0),
                                                     (100.0,-2.0,100.0, 2.0),#-9.1, -9.0
                                                    ],
                                                         
            'monitor_point'                         : 150,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 3500,
            'drawing_height'                      : 900,
            'pixel_factor'                        : 8,
        })
}