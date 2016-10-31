'''
Created on 27 Apr 2016

@author: quangv
'''

from pygame_drawing.scenario_frame import Scenario_Frame
shift = 30#85

scenarios = {             
        'narrowcorridor': Scenario_Frame({
            'name'                    : 'narrow-corridor',          

            'group'                   : 2,
            
            'group_num'               : [10,10],
            
            'group_id'                : [0,1], #it should start from 0
            
            'radius_mean'             : 0.3,
            
            'targets'                            :[(16.0,-39.0+shift)],
           
            'start_areas'                         : [
                                                     (-10.0,36.0+shift,20.0,72.0+shift), #only adjust width, do not adjust length
                                                    ],
             
            'walls'                               : [
                                                     (-11.0,1000.0+shift,-11.0, -54.0+shift),  #only adjust width, do not adjust length
                                                     (21.0,1000.0+shift,21.0, -24.0+shift),
                                                     (-11.0,-54.0+shift,1000.0, -54.0+shift),#9.1, 9.0
                                                     (21.0,-24.0+shift,1000.0,-24.0+shift),
                                                    ],
                                                         
            'monitor_point'                         : 120+shift,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 600,#2500,
            'drawing_height'                      : 400,#1200,
            'pixel_factor'                        : 8,
        })
}
