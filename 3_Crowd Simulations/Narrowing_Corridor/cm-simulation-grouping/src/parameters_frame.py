'''
Created on 27 Apr 2016

@author: quangv
'''

from pygame_drawing.scenario_frame import Scenario_Frame
shift = 70#85

scenarios = {             
        'narrowcorridor': Scenario_Frame({
            'name'                    : 'narrow-corridor',          

            'group'                   : 2,
            
            'group_num'               : [10,10],
            
            'group_id'                : [0,1], #it should start from 0
            
            'radius_mean'             : 0.3,
            
            #we shift 100 meters back
            'targets'                                :[(10000.0-shift,0.0)],

                        
            ## d1 = 30
            'start_areas'                         : [
                                                     (-70-shift,-18,-30.0-shift, 18.0), #only adjust width, do not adjust length
                                                    ],
             
            'walls'                               : [
                                                     (-500.0-shift,-19,50.0-shift, -19.0),  #only adjust width, do not adjust length
                                                     (-500.0-shift,19,50.0-shift, 19.0),
                                                     (50.0-shift,19,93.0-shift, 9.0),#9.1, 9.0
                                                     (50.0-shift,-19,93.0-shift,-9.0),#-9.1, -9.0
                                                     (93.0-shift, 9.0, 2500.0-shift, 9.0),
                                                     (93.0-shift,-9.0,2500.0-shift,-9.0),#-9.1, -9.0
                                                     
                                                    ],
                                                         
            'monitor_point'                         : 170-shift,
            
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 500,#00,#2500,#2500,
            'drawing_height'                      : 400,#900,
            'pixel_factor'                        : 8,#9,
            'shift'                                :shift, 
        
            
        })
}