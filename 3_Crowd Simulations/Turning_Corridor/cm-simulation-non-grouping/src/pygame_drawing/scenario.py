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
from src.utility.framecontext import FrameContextLog_Decoder 
from src.utility.adaptive_context import AdaptiveContextGenerator as adaptive_context
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
        self.framecontext_dir = constants.framecontext_dir        
        self.monitor_point = self.parameters['monitor_point']

        #should minus one from original since we do not allow in boundary
        self.turning_area       = Path([(-11.0,-24.0), (21.0, -24.0), (21.0,-54.0), (-11.0, -54.0)])                                                     
        self.target_final       = (1000.0,-39.0)
        self.turning_right      = 21.0                
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
               
        current_simulation_run = 0
        while current_simulation_run < 1:#len(placement_generators)/total_group_num :
            
            simulation_id = "%s" % (self.simulation_index + "_" + str(current_simulation_run+1))  
            print(">> running simulation %s" %(simulation_id))
           
            self._init_observation_plots()
            
            index = current_simulation_run*total_group_num
            
            radii_generator = radii_generators[index:index + total_group_num]
            placement_generator = placement_generators[index:index + total_group_num]
            population_generator._generate_population(radii_generator,placement_generator)  
            
            group_pedestrians = []
            if self.spawn_new_pedestrians==False:
                disp_level = self.parameters['out_group_r_strength'] / self.parameters['in_group_r_strength']
                #frame_filename = "%s" % (str(disp_level) + "_" + str(index) + "_0")
                frame_filename = "%s" % (str(index) + "_0")
                adaptivecontext_file = open("%s.json" % os.path.join(self.framecontext_dir, frame_filename))
                json_str = adaptivecontext_file.read()
                currentframecontext = json.loads(json_str, cls=FrameContextLog_Decoder)
                pedestrian_list = currentframecontext.get_pedestrian_list()            
                adaptivecontext_file.close()          
    
                additional_ped_info = dict()
                for pedestrian in pedestrian_list:
                    ped_id = pedestrian['pedestrian_id']
                    friend_zone = pedestrian['friend_zone']            
                    additional_ped_info[ped_id] = friend_zone
    
                group_pedestrians = population_generator._initialize_generated_group_pedestrians_friend_zone(additional_ped_info)
                                              
            else:
                ids_each_group = population_generator._get_ids_group()
                group_pedestrians = population_generator._initialize_generated_group_pedestrians_population(ids_each_group)
                
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
                #every pedestrian is equal, no more group id, thus we put 0
                self._canvas("draw_pedestrian", x,y,r,0)
            else:
                print("Position is unidentified")
                sys.exit()

        for s in self.parameters['start_areas']:
            self._canvas("draw_start_area", s)

        turning_draw = (-11.0,-54.0,21.0, -24.0)
        self._canvas("draw_start_area", turning_draw)
                
        for w in self.parameters['walls']:
            self._canvas("draw_wall", w)
        
        monitor = (self.monitor_point,-400,self.monitor_point,400.0)
        self._canvas("draw_wall", monitor)
            
        self._canvas("draw_text", "t = %.2f" % self.time)
               
        self.show_canvas.update()

    def _uninit_drawing(self):
        self._canvas("quit")
    
    def _done(self):
        if self.time > self.simulation_duration:
            
            pedestrian_escaped = 0
            #count pedestrians over the monitor point and printout the flow rate
            population_number = int(force_model.get_population_size())  
            for i in range(population_number):
                (x,y) = force_model.group_pedestrian_a_property(i, "position")
                if x >= self.monitor_point:
                    pedestrian_escaped+=1.0

            self.flowrate = pedestrian_escaped / self.simulation_duration            
            print("flowrate " + str(pedestrian_escaped/self.simulation_duration)) 
                   
            return True
       
        return False

    def _spawn_pedestrians(self,context_index): #re-change by spawn by file
        
        #first we get current position so that they are not overlap
        population_number = int(force_model.get_population_size())  
        current_pedestrian_position = []

        ids_each_group = []
              
        #we also need to know the current id of each group
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")
            ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
            ids_each_group.append(ped_id)
            current_pedestrian_position.append([x,y])
        
        
        if self.spawn_new_pedestrians==True:
            #we get new pedestrians
            group_num = [int(constants.spawn_rate/2), constants.spawn_rate - int(constants.spawn_rate/2)]        
            
            context = adaptive_context(self.parameters)
            context._generateContext(current_pedestrian_position, group_num)
            
            population_generator  =  PopulationGenerator(self.parameters,
                                                        self.parameters['in_group_a_strength'],self.parameters['in_group_a_range'],
                                                        self.parameters['in_group_r_strength'],self.parameters['in_group_r_range'],
                                                        self.parameters['out_group_a_strength'],self.parameters['out_group_a_range'],
                                                        self.parameters['out_group_r_strength'],self.parameters['out_group_r_range'],
                                                        self.parameters['target_a_strength'],self.parameters['target_a_range'],group_num)  
    
            radii_generator = context._get_radii_generators()
            placement_generator= context._get_placement_generators()
                                
            population_generator._generate_population(radii_generator,placement_generator,population_number)          
            additional_pedestrians, additional_id_existed_ped = population_generator._get_generated_group_pedestrians_population(ids_each_group) 

            '''we  need to add additional for existed ped here'''
            #we also need to update friend list for existed pedestrians
            for ped_id in ids_each_group:
                #we need to fetch that friend list for this pedestrian and update in model             
                current_list = additional_id_existed_ped[ped_id] 
                if len(current_list)>0:
                    current_list = [int(item) for item in current_list]
                    data = dict(ped_id=ped_id,
                            additional_count = len(current_list),
                            friend_zone = tuple(current_list))

                    force_model.add_additional_group_member(data)
                    #print(ped_id, tuple(current_list))
                                        
            '''we add new pedestrian into '''            
            if additional_pedestrians is not None and len(additional_pedestrians)>0:
                for group_member in  additional_pedestrians:                
                    force_model.add_group_pedestrian(group_member)                      
            

            #we then dump these context into folder temp_additional context
            '''dump log file by using frame'''

            frame_generator = frame_context(str(self.frames),additional_pedestrians,additional_id_existed_ped)

            disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']     
            frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
            log_file = open( "%s.json" % os.path.join(self.adaptive_context_dir, frame_filename), "w")
            json_obj = json.dumps(frame_generator, cls=FrameContextLog_Encoder)
            log_file.write(json_obj)
            log_file.close()
        
        else:    
            #we get from json file rather than add manually by code
            #the difference between two types is just group list, they should have the same placement  
            #so if self.parameters['nearby_in_group'] = 1 we have to re-assign group id for them
            disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
            #frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
            frame_filename = "%s" % (str(context_index) + "_" + str(int(self.frames)))                        
            adaptivecontext_file = open( "%s.json" % os.path.join(self.adaptive_context_dir, frame_filename))
            json_str = adaptivecontext_file.read()
            currentframecontext=  json.loads(json_str, cls=FrameContextLog_Decoder)
            pedestrian_list = currentframecontext.get_pedestrian_list()
            additional_id_existed_ped = currentframecontext.get_additional_id_existed_ped()
            adaptivecontext_file.close()

            '''we also need to dump additional for existed ped here'''
            #we also need to update friend list for existed pedestrians
            for ped_id in ids_each_group:
                #we need to fetch that friend list for this pedestrian and update in model             
                current_list = additional_id_existed_ped[str(ped_id)] 
                if len(current_list)>0:
                    current_list = [int(item) for item in current_list]
                    data = dict(ped_id=int(ped_id),
                            additional_count = len(current_list),
                            friend_zone = tuple(current_list))
                    force_model.add_additional_group_member(data)

                                                
            if pedestrian_list is not None and len(pedestrian_list)>0:
                for group_member in  pedestrian_list:                
                    force_model.add_group_pedestrian(group_member)
                       
                                                          
    def _plot_sample(self):
        
        population_number = int(force_model.get_population_size())
        
        effectiveness = []
        turning_angle = []

        #here we also measure the influential matrix of pedestrian in narrowing corridor
        influential_matrix = dict()
        
        crowd_info = dict()
        #initialize the position and id of each pedestrian
        for ped in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(ped, "position")
            ped_id = int(force_model.group_pedestrian_a_property(ped, "ped_id"))              
            crowd_info[ped_id] = (x,y)
                
        
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")            
            if math.isnan(x) ==False and math.isnan(y) ==False:
                test_in_area =  self.turning_area.contains_point((x,y))      
                if test_in_area:
                    ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))                         
                    
                    (v_x,v_y) = force_model.group_pedestrian_a_property(i,"velocity_direction")
                    
                    #select vector from desired velocity direction
                    (desired_x,desired_y) = force_model.group_pedestrian_a_property(i,"desired_direction")
                    
                    angle = self.angle_between((v_x,v_y),(desired_x,desired_y))
                    turning_angle.append(angle)
                    
                    effect =(desired_x* v_x ) + (desired_y * v_y) 
                    effectiveness.append(effect)
                    
                    #we also find the closest group member of this pedestrian
                    friend_zone =  force_model.group_pedestrian_a_property(i, "group_list")
                    friend_zone = friend_zone.split('-')
                    friend_zone = [int(friend_zone[index]) for index in range(len(friend_zone)-1)]
                    
                    #assume closest distance is the 1st friend in the list
                    friend_coordinate = crowd_info[friend_zone[0]]
                    closest_ped_distance = math.sqrt((x-friend_coordinate[0])**2 + (y-friend_coordinate[1])**2)
                    closest_ped = friend_zone[0]
                    
                    for member in friend_zone:
                        friend_coordinate = crowd_info[member]
                        temp_distance = math.sqrt((x-friend_coordinate[0])**2 + (y-friend_coordinate[1])**2)
                        if temp_distance < closest_ped_distance:
                            closest_ped_distance = temp_distance
                            closest_ped = member
                    
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
            if test_in_area or x > self.turning_right:
                data = dict(ped_index=int(i),
                            target = self.target_final)
                force_model.target_changed(data)
                #print(target)
            else:
                if x < self.turning_right:   
                    data = dict(ped_index=int(i),
                            target = self.target_original)
                    force_model.target_changed(data)
                    #print(target)
                            
    def _run(self, context_index, simulation_id, group_pedestrians): 
      
        self.time = 0.0
        self.frames = 0

        if group_pedestrians is not None and len(group_pedestrians)>0:
            for group_member in  group_pedestrians:                
                force_model.add_group_pedestrian(group_member)
                
                #pedestrian_id = group_member['pedestrian_id']  
                #friend_zone =  group_member['friend_zone']
                #print(str(pedestrian_id) + "-" + str(friend_zone))
                        
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
            
            #should get pedeestrian's friend list
            friend_zone =  force_model.group_pedestrian_a_property(i, "group_list")
            friend_zone = friend_zone.split('-')
            friend_zone = [int(friend_zone[index]) for index in range(len(friend_zone)-1)]
                
            pedestrians_frame.append(dict(
                pedestrian_id = ped_id,#
                group_id = group_id,#
                radius = r,#
                position = (x,y),#
                friend_zone = tuple(friend_zone),
                attractor_count = len(friend_zone),
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
