'''
Created on 16 Feb 2015

@author: quangv
'''
from pygame_drawing.scenario_frame import Scenario_Frame
shift_x = 40#40#85
shift_y = -10#30#85

scenarios = {             
        'narrowcorridor': Scenario_Frame({
            'name'                    : 'narrow-corridor',          

            'group'                   : 2,
            
            'group_num'               : [10,10],
            
            'group_id'                : [0,1], #it should start from 0
            
            'radius_mean'             : 0.3,
            
            'targets'                            :[(35.0-shift_x,25.0+shift_y)],
           
            'start_areas'                         : [
                                                     (-70.0-shift_x,10.0+shift_y,-40.0-shift_x,40.0+shift_y),
                                                     (110.0-shift_x,10.0+shift_y,140.0-shift_x,40.0+shift_y), 
                                                    ],
             
            'walls'                               : [
                                                     (-1000.0-shift_x,41.0+shift_y,1000.0-shift_x, 41.0+shift_y), 
                                                     (-1000.0-shift_x,9.0+shift_y,20.0-shift_x, 9.0+shift_y),
                                                     (50.0-shift_x,9.0+shift_y,1000.0-shift_x, 9.0+shift_y),
                                                     (20.0-shift_x,9.0+shift_y,20.0-shift_x,-1000.0+shift_y),
                                                     (50.0-shift_x,9.0+shift_y,50.0-shift_x,-1000.0+shift_y),
                                                    ],
                                                         
            'monitor_point'                         : -50+shift_y,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 600,#2500,
            'drawing_height'                      : 500,#1200,
            'pixel_factor'                        : 8,
        })
}