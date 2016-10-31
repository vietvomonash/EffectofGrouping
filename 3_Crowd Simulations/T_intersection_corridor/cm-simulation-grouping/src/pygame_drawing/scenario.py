'''
Created on 13 Feb 2015

@author: quangv
'''

import sys
import os, math, json
from src import constants
from src import socialforce as force_model  # @UnresolvedImport
from src.pedestrian_types.population import PopulationGenerator
from src.simulation_observations.observations import ObservationPlots as observer_plot
from src.pygame_drawing.drawing import Canvas as image_canvas
from datetime import datetime
import numpy as np
from src.utility.framecontext import FrameContext as frame_context
from src.utility.framecontext import FrameContextLog_Encoder 
from src.utility.adaptive_context import AdaptiveContextGenerator as adaptive_context
from src.utility.adaptive_context import AdaptiveContextLog_Encoder
from src.utility.adaptive_context import AdaptiveContextLog_Decoder
from matplotlib.path import Path

class Scenario:
    
    
    def __init__(self, parameters = {}):
        
        self.parameters = parameters
        
        self.timestep = constants.timestep
        self.parameters['timestep'] = self.timestep      
        self.simulation_duration = constants.total_monitoring_duration_uni_direction
           
        self.parameters['constant_target'] = 1
        self.parameters['constant_target_magnitude'] = 2.6
        
        self.frame_save_frequency = int(constants.frame_store_sample_frequency/self.timestep)
        self.spawn_frequency = int(constants.spawn_pedestrian_frequency/self.timestep)  
        self.adaptive_context_dir = constants.adaptive_dir
        self.monitor_point = self.parameters['monitor_point']
        
        self.turning_area       = Path([(20.0,41.0), (50.0, 41.0), (50.0,9.0), (20.0, 9.0)])                                                     
        self.target_final       = (35.0,-1000.0)
        self.turning_up         = 9.0                
        self.target_original    = self.parameters['targets'][0]                        

                                                     
    def run_aggregate(self,
                        in_group_a_strength, in_group_a_range,
                        in_group_r_strength, in_group_r_range,
                        out_group_a_strength, out_group_a_range, 
                        out_group_r_strength, out_group_r_range,
                        target_a_strength, target_a_range,
                        context, 
                        spawn_new_pedestrians=False, 
                        simulation = True,drawing=True):

        """ initialize social force model """
        force_model.set_parameters(self.parameters)
        self.spawn_new_pedestrians=spawn_new_pedestrians
                     
        self.drawing = drawing                            
        total_group_num = len(self.parameters['group_num'])       
        
        
        ''' set parameter '''
        self.parameters['in_group_a_strength'] = in_group_a_strength
        self.parameters['in_group_a_range'] = in_group_a_range
        self.parameters['in_group_r_strength'] = in_group_r_strength
        self.parameters['in_group_r_range'] = in_group_r_range
        self.parameters['out_group_a_strength'] = out_group_a_strength
        self.parameters['out_group_a_range'] = out_group_a_range
        self.parameters['out_group_r_strength'] = out_group_r_strength
        self.parameters['out_group_r_range'] = out_group_r_range
        self.parameters['target_a_strength'] = target_a_strength
        self.parameters['target_a_range'] = target_a_range
    
        self.flowrate_simulations = []
        self.flowrate = 0

        #we only measure pedestrians inside this area
        self.turning_angles = []
        self.effective_evacuation = []
                                        
        self.simulation_index = "%s" % str(datetime.now().microsecond)  
            
        population_generator  =  PopulationGenerator(self.parameters,
                                                    in_group_a_strength, in_group_a_range,
                                                    in_group_r_strength, in_group_r_range,
                                                    out_group_a_strength, out_group_a_range, 
                                                    out_group_r_strength, out_group_r_range,
                                                    target_a_strength, target_a_range)         
                 
        """ perform simulation over context_placement_num"""
        radii_generators = context._get_radii_generators()
        placement_generators= context._get_placement_generators()
        t = len(placement_generators)       
        current_simulation_run = 0
        while current_simulation_run < 1:#len(placement_generators)/total_group_num :
            
            simulation_id = "%s" % (self.simulation_index + "_" + str(current_simulation_run+1))  
            print(">> running simulation %s" %(simulation_id))
           
            self._init_observation_plots()
            
            index = current_simulation_run*total_group_num
            radii_generator = radii_generators[index:index + total_group_num]
            placement_generator = placement_generators[index:index + total_group_num]
            generated_group_member_index = population_generator._generate_population(radii_generator,placement_generator)  
            group_pedestrians1 = population_generator._get_generated_group_pedestrians_population()              
            
            bio_index = int(len(radii_generators)/2) + index
            radii_generator = radii_generators[bio_index:bio_index + total_group_num]
            placement_generator = placement_generators[bio_index:bio_index + total_group_num]
            population_generator._generate_population(radii_generator,placement_generator,generated_group_member_index)  
            group_pedestrians2 = population_generator._get_generated_group_pedestrians_population()    
            
            group_pedestrians =   group_pedestrians1 +  group_pedestrians2                     

            self._run(index, simulation_id, group_pedestrians) 

            self.plots._dump_influential_matrix(current_simulation_run)
            
            self.flowrate_simulations.append(self.flowrate)
                           
            #turning_angels
            angels = self.plots.get_turning_angles()
            #print(angels)
            for item in angels:
                self.turning_angles.append(item)         
   
            #get effective evacuation
            effectiveness = self.plots.get_effective_evacuation()
            #print(effectiveness)
            for item in effectiveness:
                self.effective_evacuation.append(item)    
            
            self.plots.reset_sample()
            
            force_model.reset_model()
            self.flowrate = 0
            
            current_simulation_run+=1
    
    def _init_observation_plots(self):
        self.sample_frequency = int(constants.plot_sample_frequency/self.timestep)
        self.plots = observer_plot(self.parameters)
        self.observation_plot_prefix = os.path.join(constants.observation_dir, self.parameters['name'])
           
    def _init_drawing(self, simulation_id):
        self.show_canvas = image_canvas(
                    self.parameters['drawing_width'],
                    self.parameters['drawing_height'],
                    self.parameters['pixel_factor'])
         
    def _tick(self):
        return self._canvas("tick", constants.framerate_limit)
    
    def _canvas(self, method, *args):
        return getattr(self.show_canvas, method)(*args)
    
    def _draw(self):
        self._canvas("clear_screen")

        group_population_number = int(force_model.get_population_size())
        for i in range(group_population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")
            if math.isnan(x) ==False and math.isnan(y)==False:
                r = force_model.group_pedestrian_a_property(i, "radius")
                group_id = force_model.group_pedestrian_a_property(i, "groupid")
                self._canvas("draw_pedestrian", x,y,r,group_id)
            else:
                print("Position is unidentified")
                sys.exit()

        for s in self.parameters['start_areas']:
            self._canvas("draw_start_area", s)

        turning_draw = (20.0,9.0,50.0, 41.0)
        self._canvas("draw_start_area", turning_draw)
                
        for w in self.parameters['walls']:
            self._canvas("draw_wall", w)

        monitor = (-1000,self.monitor_point,1000.0,self.monitor_point)
        self._canvas("draw_wall", monitor)
               
        #self._canvas("draw_target", self.parameters['targets'][0][0], self.parameters['targets'][0][1])
                            
        self._canvas("draw_text", "t = %.2f" % self.time)
               
        self.show_canvas.update()
   
    def _uninit_drawing(self):
        self._canvas("quit")
    
    def _done(self):
        if self.time > self.simulation_duration:
            
            pedestrian_escaped = 0
            # count pedestrians over the monitor point and printout the flow rate
            population_number = int(force_model.get_population_size())  
            for i in range(population_number):
                (x, y) = force_model.group_pedestrian_a_property(i, "position")
                if y <= self.monitor_point:
                    pedestrian_escaped += 1.0        
            
            self.flowrate = pedestrian_escaped / self.simulation_duration
            print("flowrate " + str(pedestrian_escaped / self.simulation_duration))     
                        
            return True
       
        return False

    def _spawn_pedestrians(self,context_index): #re-change by spawn by file
        
        #first we get current position so that they are not overlap
        population_number = int(force_model.get_population_size())  
        current_pedestrian_position = []
        group_num = [int(constants.spawn_rate/2), constants.spawn_rate - int(constants.spawn_rate/2)]  
        
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")
            current_pedestrian_position.append([x,y])
  
        if self.spawn_new_pedestrians==True:
            context1 = adaptive_context(self.parameters)
            context1._generateContext(current_pedestrian_position, group_num,self.parameters['start_areas'][0])
            
            context2 = adaptive_context(self.parameters)
            context2._generateContext(current_pedestrian_position, group_num,self.parameters['start_areas'][1])           
            
        else:          
            #we get from json file rather than add manually by code
            disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
            #frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
            frame_filename = "%s" % (str(context_index) + "_" + str(int(self.frames)))
                                
            adaptivecontext_file1 = open( "%s_1.json" % os.path.join(self.adaptive_context_dir, frame_filename))
            json_str = adaptivecontext_file1.read()
            context1=  json.loads(json_str, cls =AdaptiveContextLog_Decoder)
            adaptivecontext_file1.close()
        
            
            adaptivecontext_file2 = open( "%s_2.json" % os.path.join(self.adaptive_context_dir, frame_filename))
            json_str = adaptivecontext_file2.read()
            context2=  json.loads(json_str, cls =AdaptiveContextLog_Decoder)
            adaptivecontext_file2.close()
                        
        population_generator  =  PopulationGenerator(self.parameters,
                                                    self.parameters['in_group_a_strength'],self.parameters['in_group_a_range'],
                                                    self.parameters['in_group_r_strength'],self.parameters['in_group_r_range'],
                                                    self.parameters['out_group_a_strength'],self.parameters['out_group_a_range'],
                                                    self.parameters['out_group_r_strength'],self.parameters['out_group_r_range'],
                                                    self.parameters['target_a_strength'],self.parameters['target_a_range'],group_num)  

        radii_generator1 = context1._get_radii_generators()
        placement_generator1= context1._get_placement_generators()
                            
        pedestrian_current_id = population_generator._generate_population(radii_generator1,placement_generator1,population_number)          
        additional_pedestrians1 = population_generator._get_generated_group_pedestrians_population() 
        if additional_pedestrians1 is not None and len(additional_pedestrians1)>0:
            for group_member in  additional_pedestrians1:                
                force_model.add_group_pedestrian(group_member)                      
        
        radii_generator2 = context2._get_radii_generators()
        placement_generator2= context2._get_placement_generators()
                
        population_generator._generate_population(radii_generator2,placement_generator2,pedestrian_current_id)          
        additional_pedestrians2 = population_generator._get_generated_group_pedestrians_population() 
        if additional_pedestrians2 is not None and len(additional_pedestrians2)>0:
            for group_member in  additional_pedestrians2:                
                force_model.add_group_pedestrian(group_member)                      
   
           
        if self.spawn_new_pedestrians==True:
        #we then dump these context into folder temp_additional context
            disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
            frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
        
            log_file = open( "%s_1.json" % os.path.join(self.adaptive_context_dir, frame_filename), "w")
            json_obj = json.dumps(context1, cls=AdaptiveContextLog_Encoder)
            log_file.write(json_obj)
            log_file.close()
        
            frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
        
            log_file = open( "%s_2.json" % os.path.join(self.adaptive_context_dir, frame_filename), "w")
            json_obj = json.dumps(context2, cls=AdaptiveContextLog_Encoder)
            log_file.write(json_obj)
            log_file.close()            

    def _plot_sample(self):
        
        population_number = int(force_model.get_population_size())  

        effectiveness = []
        turning_angle = []

        #here we also measure the influential matrix of pedestrian in narrowing corridor
        influential_matrix = dict()
        crowd_info =  [[] for i in range(2)] #since we have 2 groups
        #initialize the position and id of each pedestrian
        
        for ped in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(ped, "position")
            ped_id = int(force_model.group_pedestrian_a_property(ped, "ped_id"))   
            group_id =  int(force_model.group_pedestrian_a_property(ped, "groupid"))          
            crowd_info[group_id].append([ped_id,x,y])
                
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")
            if math.isnan(x) ==False and math.isnan(y) ==False:                      

                test_in_area =  self.turning_area.contains_point((x,y))      
                if test_in_area:
                    (v_x,v_y) = force_model.group_pedestrian_a_property(i,"velocity_direction")
                    
                    #select vector from desired velocity direction
                    (desired_x,desired_y) = force_model.group_pedestrian_a_property(i,"desired_direction")
                    
                    angle = self.angle_between((v_x,v_y),(desired_x,desired_y))
                    turning_angle.append(angle)
                    
                    effect =(desired_x* v_x ) + (desired_y * v_y) 
                    effectiveness.append(effect)
                    
                                        
                    ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
                    group_id =  int(force_model.group_pedestrian_a_property(i, "groupid"))                        
                    
                    closest_distance = 999
                    closest_ped = -1
                    #find the nearest pedestrian in the list
                    for member in crowd_info[group_id]:
                        if member[0] != ped_id:                 
                            temp_distance = math.sqrt((x-member[1])**2 + (y-member[2])**2)
                            if temp_distance < closest_distance:
                                closest_distance = temp_distance
                                closest_ped = member[0]
                                
                    
                    influential_matrix[ped_id] = closest_ped
                

        total_effective = 0
        if len(effectiveness)>0:
            total_effective = np.sum(effectiveness)
            total_effective /=len(effectiveness)
               
        self.plots._add_new_sample(turning_angle,total_effective,influential_matrix)


    def _revise_target(self):
                
        population_number = int(force_model.get_population_size())  
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")                    
            test_in_area =  self.turning_area.contains_point((x,y))
            if test_in_area or y < self.turning_up:
                data = dict(ped_index=int(i),
                            target = self.target_final)
                force_model.target_changed(data)

            else:
                if y > self.turning_up:   
                    data = dict(ped_index=int(i),
                            target = self.target_original)
                    force_model.target_changed(data)
                     
    def _run(self, context_index, simulation_id, group_pedestrians): 
      
        self.time = 0.0
        self.frames = 0

        if group_pedestrians is not None and len(group_pedestrians)>0:
            for group_member in  group_pedestrians:                
                force_model.add_group_pedestrian(group_member)
                        
        self._init_drawing(simulation_id)
               
        finished = False
                        
        try:
            while self._tick() and not finished:
                force_model.update_pedestrians()

                if self.drawing: 
                    self._draw()
                
                if (not self.frames % self.sample_frequency):
                    self._plot_sample()
              
                if (not self.frames % self.frame_save_frequency):
                    self._dump_frame(context_index,self.frames)
                
                self._revise_target()
                
                if (not self.frames % self.spawn_frequency):
                    self._spawn_pedestrians(context_index)
   
                self.time += self.timestep
                self.frames += 1

                if self._done():
                    finished = True
                
        except KeyboardInterrupt:
            pass

        if self.drawing:
            self._uninit_drawing()

    def _dump_frame(self, context_index, current_frame):
        population_number = int(force_model.get_population_size())  

        pedestrians_frame = []

        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")
            r = force_model.group_pedestrian_a_property(i, "radius")
            group_id = force_model.group_pedestrian_a_property(i, "groupid")
            ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
            (target_x,target_y) = force_model.group_pedestrian_a_property(i, "target")
            
            pedestrians_frame.append(dict(
                pedestrian_id = ped_id,#
                group_id = group_id,#
                radius = r,#
                position = (x,y),#
                
                in_group_a_strength = self.parameters['in_group_a_strength'],#
                in_group_a_range = self.parameters['in_group_a_range'] ,#
                in_group_r_strength = self.parameters['in_group_r_strength'],#
                in_group_r_range = self.parameters['in_group_r_range'],
                
                out_group_a_strength = self.parameters['out_group_a_strength'],#
                out_group_a_range = self.parameters['out_group_a_range'],
                out_group_r_strength = self.parameters['out_group_r_strength'],
                out_group_r_range = self.parameters['out_group_r_range'],
                
                #target point
                target =  (target_x,target_y),#
                target_a_strength = self.parameters['target_a_strength'],
                target_a_range = self.parameters['target_a_range']))#
            
        frame_generator = frame_context(current_frame,pedestrians_frame)              
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(current_frame))
         
        log_file = open( "%s.json" % os.path.join(constants.framecontext_dir, frame_filename), "w")
        json_obj = json.dumps(frame_generator, cls=FrameContextLog_Encoder)
        log_file.write(json_obj)
        log_file.close()
                             
    def _get_parameters(self):
        return self.parameters
    
    def _get_flowrate_simulations(self):
        return self.flowrate_simulations

    def _get_turning_angles(self):
        return self.turning_angles
    
    def _get_effective(self):
        return self.effective_evacuation
        
    """ Returns the unit vector of the vector.  """
    def unit_vector(self,vector):
        return vector / np.linalg.norm(vector)  
    
    def angle_between(self,v1, v2):
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        rad = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        return math.degrees(rad)  
            