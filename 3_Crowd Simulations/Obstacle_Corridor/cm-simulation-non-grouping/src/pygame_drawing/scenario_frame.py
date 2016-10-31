'''
Created on 27 Apr 2016

@author: quangv
'''


import sys
import os, math, json
from src import constants
from src import socialforce as force_model  # @UnresolvedImport
from src.pygame_drawing.drawing import Canvas as image_canvas
from src.utility.framecontext import FrameContextLog_Decoder 
from src.simulation_observations.pedestrian_track import Pedestrian_Track
from src.pedestrian_types.population import PopulationGenerator
from src.utility.adaptive_context import AdaptiveContextGenerator as adaptive_context
from src.utility.adaptive_context import AdaptiveContextLog_Encoder
from src.utility.adaptive_context import AdaptiveContextLog_Decoder
from matplotlib.path import Path

class Scenario_Frame:
        
    def __init__(self, parameters = {}):
        
        self.parameters = parameters
        
        self.timestep = constants.timestep
        self.parameters['timestep'] = self.timestep
        self.simulation_duration = constants.total_monitoring_duration_uni_direction
        self.shift = self.parameters['shift']

        self.spawn_frequency = int(constants.spawn_pedestrian_frequency/self.timestep)  
        self.adaptive_context_dir = constants.adaptive_dir
        self.monitor_point = self.parameters['monitor_point']
                
        self.x_vertical_line = 80.0-self.shift
        self.y_horizontal_line = 0.0
        self.target_upper    = (80.0-self.shift,-12.0)         
        self.target_below   = (80.0-self.shift,12.0)
        self.target_final    = self.parameters['targets'][0]  
        
        self.split_area =  Path([(20.0-self.shift,25.0), (60.0-self.shift, 25.0), (60.0-self.shift,-25.0), (20.0-self.shift, -25.0)])
        self.merge_area =  Path([(100.0-self.shift,25.0), (140.0-self.shift, 25.0), (140.0-self.shift,-25.0), (100.0-self.shift, -25.0)])    
                        
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
                ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
                     
                is_tracked = self._canvas("is_tracked_pedestrian", x,y)
                
                if (is_tracked and constants.tracked_pedestrian_id== -1) :
                    self._canvas("reset_tracked_position")
                    constants.tracked_pedestrian_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
           
                    self.pedestrian_track._reset(self.time, constants.tracked_pedestrian_id)
                    self.pedestrian_track._force_color('r.-','k.-')
                    self.draw_tracked_ped()
                    
                else:
                    if  constants.tracked_pedestrian_id == ped_id : #break in order to not depend on i
                        self.draw_tracked_ped()
                
                    else:       
                        self._canvas("draw_pedestrian", x,y,r,0)
            else:
                print("Position is unidentified")
                sys.exit()

        for s in self.parameters['start_areas']:
            self._canvas("draw_start_area", s)

        #monitor = (self.monitor_point,-40,self.monitor_point,40.0)
        #self._canvas("draw_wall", monitor)
                
        for w in self.parameters['walls']:
            self._canvas("draw_wall", w)
            
        split_draw =  (20.0-self.shift, -25.0, 60.0-self.shift, 25.0)#(60.0, -19.0, 80.0, 19.0)
        merge_draw =  (100.0-self.shift, -25.0, 140.0-self.shift, 25.0)#(130.0, -19.0,150.0, 19.0)
                                                                                                        
        obstacle = (60.0-self.shift,-2,100.0-self.shift, 2.0)
        
        #self._canvas("draw_start_area", split_draw)
        #self._canvas("draw_start_area", merge_draw)        
                        
        self._canvas("draw_obstacle", obstacle)                
                        
        monitor = (self.monitor_point,-40,self.monitor_point,40.0)
        self._canvas("draw_wall", monitor)
                    
        #self._canvas("draw_text", "t = %.2f" % self.time)
        
        self.show_canvas.update()

    def _uninit_drawing(self):
        self._canvas("quit")
    
    def _spawn_pedestrians(self,context_index): #re-change by spawn by file
        
        #first we get current position so that they are not overlap
        population_number = int(force_model.get_population_size())  
        ids_each_group = []
                
        for i in range(population_number):
            ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
            ids_each_group.append(ped_id)
             
        #we get from json file rather than add manually by code
        disp_level = self.parameters['out_group_r_strength']/self.parameters['in_group_r_strength']
        #frame_filename = "%s" % (str(disp_level) + "_" + str(context_index) + "_" + str(int(self.frames)))
        #frame_filename = "%s" % (str(context_index) + "_" + str(int(self.frames)))            
        frame_filename = "%s" % (str(self.parameters['in_group_r_strength']) + "_" + str(self.parameters['in_group_a_strength']) + "_" + str(disp_level) + "_" + 
                                     str(context_index) + "_" + str(int(self.frames)))        
        
        adaptivecontext_file = open( "%s.json" % os.path.join(self.adaptive_context_dir,frame_filename))
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
         
        '''update position and target shift for pedestrian list '''            
        if pedestrian_list is not None and len(pedestrian_list)>0:
            for pedestrian in pedestrian_list:                
                position = (pedestrian['position'][0]-self.shift,pedestrian['position'][1])#
                del pedestrian['position']
                pedestrian['position'] = position
                
                target =  (pedestrian['target'][0]-self.shift,pedestrian['target'][1])#
                del pedestrian['target']
                pedestrian['target'] = target

        if pedestrian_list is not None and len(pedestrian_list)>0:
            for group_member in  pedestrian_list:
                (x,y) = group_member['position']              
                if y <= self.y_horizontal_line:
                    del group_member['target']
                    group_member['target'] = self.target_upper
                else:                                                                
                    del group_member['target']
                    group_member['target'] = self.target_below
                                            
                force_model.add_group_pedestrian(group_member)   

    def _done(self):
        
        if self.time > self.simulation_duration:
            pedestrian_escaped = 0
            # count pedestrians over the monitor point and printout the flow rate
            population_number = int(force_model.get_population_size())  
            for i in range(population_number):
                (x, y) = force_model.group_pedestrian_a_property(i, "position")
                if x >= self.monitor_point:
                    pedestrian_escaped += 1.0        
            
            print("flowrate " + str(pedestrian_escaped / self.simulation_duration))   

            return True
        
        return False

    def _revise_target(self):
                
        population_number = int(force_model.get_population_size())  
        for i in range(population_number):
            (x,y) = force_model.group_pedestrian_a_property(i, "position")                    
            if x >= self.x_vertical_line:
                data = dict(ped_index=int(i),
                            target = self.target_final)
                force_model.target_changed(data)
                
    def replay_frame(self,constant, index_simulation, time_replay,constant_target,constant_target_magnitude,
                     in_group_a_strength, in_group_a_range,
                     in_group_r_strength, in_group_r_range):
     
        frame = (time_replay / constants.frame_store_sample_frequency) * ( constants.frame_store_sample_frequency/constants.timestep)
        intframe = int(frame)
        #filename = str(constant) + "_" + str(index_simulation) + "_" + str(intframe)
        filename = "%s" % (str(in_group_r_strength) + "_" + str(in_group_a_strength) + "_" + str(constant) + "_" + 
                                     str(index_simulation) + "_" + str(intframe))    
                
        index_simulation = index_simulation*2
        #filename =  str(index_simulation) + "_" + str(intframe)
        frame_log_file = open( "%s.json" % os.path.join(constants.framecontext_dir, filename))

        json_str = frame_log_file.read()
        currentframecontext=  json.loads(json_str, cls =FrameContextLog_Decoder)

        pedestrian_list = currentframecontext.get_pedestrian_list()

        ''' set parameter '''
        self.in_group_a_strength = in_group_a_strength
        self.in_group_a_range =  in_group_a_range
        self.in_group_r_strength = in_group_r_strength
        self.in_group_r_range = in_group_r_range
        
        self.parameters['in_group_a_strength'] = in_group_a_strength
        self.parameters['in_group_a_range'] = in_group_a_range
        self.parameters['in_group_r_strength'] = in_group_r_strength
        self.parameters['in_group_r_range'] = in_group_r_range
        self.parameters['out_group_a_strength'] = self.parameters['in_group_a_strength'] * (1/constant)
        self.parameters['out_group_a_range'] = self.parameters['in_group_a_range']
        self.parameters['out_group_r_strength'] = self.parameters['in_group_r_strength'] * constant
        self.parameters['out_group_r_range'] = self.parameters['in_group_r_range']
        self.parameters['target_a_strength'] = 22000000000
        self.parameters['target_a_range'] = 435
        

        self.parameters['constant_target'] = constant_target
        self.parameters['constant_target_magnitude'] = constant_target_magnitude
        
                                
        '''update position and target shift for pedestrian list '''
        for pedestrian in pedestrian_list:
            position = (pedestrian['position'][0]-self.shift,pedestrian['position'][1])#
            del pedestrian['position']
            pedestrian['position'] = position
            
            target =  (pedestrian['target'][0]-self.shift,pedestrian['target'][1])#
            del pedestrian['target']
            pedestrian['target'] = target
        
        simulation_id = "Replay frame"

        """ initialize social force model """
        force_model.set_parameters(self.parameters)
        force_model.set_start_simulation_time(time_replay) 

        self.time = time_replay
        self.frames = frame
        
        if pedestrian_list is not None and len(pedestrian_list)>0:
            for group_member in pedestrian_list:                
                '''should modify target position based on y'''
                (x,y) = group_member['position']
                if y <= self.y_horizontal_line:
                    del group_member['target']
                    group_member['target'] = self.target_upper
                else:                                                                
                    del group_member['target']
                    group_member['target'] = self.target_below
                
                force_model.add_group_pedestrian(group_member)
                
        
        self._init_drawing(simulation_id)
               
        finished = False
        
        ###IMPORTANT PART FOR SHARED OBJECT
        constants.tracked_pedestrian_id = -1  
         
        """ initialize the real-time plot """
        self.pedestrian_track = Pedestrian_Track(self.time)   
        self.tracking_sample_frequency = int(constants.plot_sample_frequency/(2*self.timestep))
        count = 0                        
        try:
            while self._tick() and not finished:
                force_model.update_pedestrians()

                self._draw()

                self._revise_target()
                
                if (not self.frames % self.spawn_frequency):
                    self._spawn_pedestrians(index_simulation)

                #if (not self.frames % self.tracking_sample_frequency):
                #    self._plot_track_ped()
                self.show_canvas.create_image(count)#self.frames)   
                count+=1
                                                                                          
                self.time += self.timestep
                self.frames += 1
                
                if self._done():
                    finished = True
                
        except KeyboardInterrupt:
            pass

        self._uninit_drawing()
            
    def draw_tracked_ped(self):
 
        target_vector = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "target_vector")
        ingroup_vector = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "ingroup_vector")
        outgroup_vector = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "outgroup_vector")
        wall_vector = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "wall_vector")   
        
        (x,y) = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "position")
        r = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "radius")
        group_id = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "groupid")
                    
        if math.isnan(x) ==False and math.isnan(y)==False:
            self._canvas("draw_pedestrian_tracking", x,y,r,group_id,
                                         target_vector,
                                         ingroup_vector,
                                         outgroup_vector,
                                         wall_vector)

        
    def _plot_track_ped(self):
        
        if constants.tracked_pedestrian_id != -1:

            target_force = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "target_force")
            if target_force != -999.0:
            
                wall_force = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "wall_force")
                ingroup_force = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "ingroup_force")
                outgroup_force  = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "outgroup_force")  
                velocity_x = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id,"velocity_x")
                speed =   force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id,"velocity")                
                (x,y) = force_model.group_pedestrian_id_property(constants.tracked_pedestrian_id, "position")
                current_position = int(round(x + self.shift))# +30
                
                #plot for force and velocity based on time     
                #self.pedestrian_track._addsample(self.time , target_force, ingroup_force, outgroup_force, wall_force,velocity_x,current_position)
                self.pedestrian_track._addsample(self.time , target_force, ingroup_force, outgroup_force, wall_force,speed,current_position)
                 

        data = []
        group_population_number = int(force_model.get_population_size())

        for i in range(group_population_number):
                ped_id = int(force_model.group_pedestrian_a_property(i, "ped_id"))
                target_force = force_model.group_pedestrian_a_property(i, "target_force")
                ingroup_force = force_model.group_pedestrian_a_property(i, "ingroup_force")                
                outgroup_force  = force_model.group_pedestrian_a_property(i, "outgroup_force")    
                wall_force = force_model.group_pedestrian_a_property(i, "wall_force")
                
                velocity_x = force_model.group_pedestrian_a_property(i,"velocity_x")
                speed =   force_model.group_pedestrian_id_property(i,"velocity")
                (x,y) = force_model.group_pedestrian_a_property(i, "position")
                current_position = int(round(x + self.shift)) #+30
 
                 
                #data.append([ped_id,target_force,ingroup_force,outgroup_force,wall_force,velocity_x,current_position])
                data.append([ped_id,target_force,ingroup_force,outgroup_force,wall_force,speed,current_position])
                         
                        
        self.pedestrian_track._addsample2(self.time , data)
                         
    def _get_parameters(self):
        return self.parameters