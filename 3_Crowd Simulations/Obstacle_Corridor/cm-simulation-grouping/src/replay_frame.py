'''
Created on 26 Apr 2016

@author: quangv
'''
import parameters_frame


parameters_frame.shift = 85

monte_carlos_simulation = parameters_frame.scenarios['narrowcorridor']
constant =1.4

############################ DO NOT CHANGE
constant_target = 1
constant_target_magnitude = 2.6

 
index_simulation= 0
time_replay = 80#80
  
    
monte_carlos_simulation.replay_frame(constant, index_simulation, time_replay,constant_target,constant_target_magnitude,
                                     in_group_a_strength=16, in_group_a_range=2.8,
                                     in_group_r_strength=36, in_group_r_range=2.0)
