'''
Created on 27 Apr 2016

@author: quangv
'''

from pygame_drawing.scenario_frame import Scenario_Frame
shift = 63#75

scenarios = {             
        'narrowcorridor': Scenario_Frame({
            'name'                    : 'narrow-corridor',          

            'group'                   : 2,
            
            'group_num'               : [10,10],
            
            'group_id'                : [0,1], #it should start from 0
            
            'radius_mean'             : 0.3,
            
            #we shift 100 meters back
            'targets'                                :[(10000.0-shift,0.0)],

            #note that -30 = 0            
            ## d1 = 30
            'start_areas'                         : [
                                                     (-70-shift,-24,-30.0-shift, 24.0),
                                                    ],
                                          
            'walls'                               : [
                                                     (-500.0-shift,-25,500.0-shift, -25.0),  #only adjust width, do not adjust length
                                                     (-500.0-shift,25,500.0-shift, 25.0),
                                                     (60.0-shift,2,100.0-shift, 2.0),#9.1, 9.0
                                                     (60.0-shift,-2,100.0-shift,-2.0),
                                                     (60.0-shift, -2.0, 60.0-shift, 2.0),
                                                     (100.0-shift,-2.0,100.0-shift, 2.0),#-9.1, -9.0
                                                                                               
                                                     ],
            'monitor_point'                         : 150-shift,
                        
            'w_R'                                   : 500,
            'w_r'                                   : 2.0,
            'drawing_width'                       : 600,
            'drawing_height'                      : 400,
            'pixel_factor'                        : 7,
            'shift'                                :shift,             
        })
}
