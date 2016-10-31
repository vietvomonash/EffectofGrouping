import parameters
from src.utility.context import ContextLog_Decoder 
import os, json
from src import constants

monte_carlos_simulation = parameters.scenarios['narrowcorridor']
context_log_file = open( "%s.json" % os.path.join(constants.context_dir, "context_longcorridor_50"))

json_str = context_log_file.read()
context=  json.loads(json_str, cls =ContextLog_Decoder)

in_group_r_strength = 36  #[34.0,36.0,38.0,42.0,44.0]
in_group_r_range = 2.0
in_group_a_strength = 16#18 #[16.0,17.0,18,19.0,20.0]
in_group_a_range = 2.8
target_a_strength= 22000000000
target_a_range = 435

''' should not be 1.0 because we want to break the symmetric '''
c = 1.4#2.0  #[1.4,1.6,1.8,2.0]
 
out_group_r_strength = in_group_r_strength * c
out_group_r_range = in_group_r_range
out_group_a_strength = in_group_a_strength * (1/c)
out_group_a_range = in_group_a_range 

monte_carlos_simulation.run_aggregate(in_group_a_strength, in_group_a_range,
                                      in_group_r_strength, in_group_r_range,
                                      out_group_a_strength, out_group_a_range, 
                                      out_group_r_strength, out_group_r_range,
                                      target_a_strength, target_a_range,
                                      context,
                                      spawn_new_pedestrians=True,
                                      simulation=True, drawing=True)
