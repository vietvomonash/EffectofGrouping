'''
Created on 26 Apr 2016

@author: quangv
'''
import parameters_frame

monte_carlos_simulation = parameters_frame.scenarios['narrowcorridor']

constant =1.4

############################ DO NOT CHANGE
constant_target = 1
constant_target_magnitude = 2.6

 
index_simulation= 0
time_replay = 60
  
    
monte_carlos_simulation.replay_frame(constant, index_simulation, time_replay,constant_target,constant_target_magnitude)
