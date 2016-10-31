'''
Created on 13 Feb 2015

@author: quangv
'''
import pygame
from pygame import gfxdraw
from src import constants 
from math import hypot
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = str(700) + "," + str(80) #x,y coordination

BG_WHITE_COLOUR = (255,255,255)
DRAW__DARK_COLOUR = (0,0,0)
TARGET_PINK__COLOUR = (255,0,127)

START_AREA_COLOUR = (148,154,70)
TRACKING_AREA_COLOUR = (153,153,0)

TARGET_FORCE__COLOUR = (0,0,255) #blue 
INTERACTION_FORCE__COLOUR = (255,0,0) #red
OBSTACLE_FORCE__COLOUR = (102,204,0) #green
TRAIL_COLOUR = (153,0,0)
COLOURS = [
        (0,0,0),#black
        (255,0,0), # red color
        (0,0,255), # blue color
        (102,204,0), # green color
        (153,0,76), #yellow color for average cutoff level3 pedestrian
        (255,128,0),#brown color for average cutoff level1 pedestrian
        (204,102,0),#orange color for uniform cutoff level3 pedestrian
        (0,204,204),# light blue color for uniform cutoff level1 pedestrian
        ]
class Canvas:
    """This class is to manage canvas and its object """
    def __init__(self, width, height, factor):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption("Group Behavior")
        self.pixel_factor = factor
        
        self.target_colours = dict()
        self.font = pygame.font.Font(None, 18)
        self.clock = pygame.time.Clock()

        self.pedestrian_pos_track = [-999.0,-999.0]
        
        self.threshold_track_pedestrian_pos = 0.5 #this value is used to find pedestrian ID when user clicks on simulation environment

                
    def quit(self):
        pygame.display.quit()
    
    def clear_screen(self):
        self.screen.fill(BG_WHITE_COLOUR)
        
    def tick(self,framerate):
        self.clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.pedestrian_pos_track = pygame.mouse.get_pos()
                self.pedestrian_pos_track = self.convert_pos_coords(self.pedestrian_pos_track[0],self.pedestrian_pos_track[1])
                constants.tracked_pedestrian_id = -1

                
        return True  
    
    def update(self):
        pygame.display.flip()
               
    def _draw_circle(self, x, y, radii, color):       
        gfxdraw.aacircle(self.screen, x, y, radii, color)    
    
    def _draw_filled_circle(self,x,y,radii,color):
        gfxdraw.filled_circle(self.screen, x, y, radii, color)    
                   
    def _draw_line(self, x1, y1, x2, y2, c):
        gfxdraw.line(self.screen, x1, y1, x2, y2, c)

    def draw_wall(self, w):
        (x1,y1) = self.screen_coords(w[0], w[1])
        (x2,y2) = self.screen_coords(w[2], w[3])
        self._draw_line(x1, y1, x2, y2, DRAW__DARK_COLOUR)
    
    def draw_suspected_area(self, w):
        (x1,y1) = self.screen_coords(w[0], w[1])
        (x2,y2) = self.screen_coords(w[2], w[3])
        self._draw_line(x1, y1, x2, y2, TRAIL_COLOUR)
        
    def _get_colour(self, t):
        if not t in self.target_colours:
            self.target_colours[t] = COLOURS[len(self.target_colours)]
        return self.target_colours[t]
    
    def draw_start_area(self, t):
        (x1,y1) = self.screen_coords(t[0], t[1])
        (x2,y2) = self.screen_coords(t[2], t[3])
        pygame.draw.rect(self.screen, START_AREA_COLOUR, (x1, y1, x2-x1, y2-y1),1)
      
    def draw_force_tracking_area(self, m):
        (x1,y1) = self.screen_coords(m[0], m[1])
        (x2,y2) = self.screen_coords(m[2], m[3])
        pygame.draw.rect(self.screen, TRACKING_AREA_COLOUR, (x1, y1, x2-x1, y2-y1),1)
            
    def draw_group_center(self,group_center_x,group_center_y):
        group_center_x = constants.myround(group_center_x,4)
        group_center_y = constants.myround(group_center_y,4)
        (group_center_x,group_center_y) = self.screen_coords(group_center_x,group_center_y)
        pygame.draw.circle(self.screen, TRACKING_AREA_COLOUR, (group_center_x,group_center_y), self.screen_radius(0.2), 0)
        
    def create_image(self, simulationId):
        ext = "jpeg"
        pygame.image.save(self.screen, "%s%s.%s" % (constants.image_dir, simulationId, ext))
        
    def draw_pedestrian(self, x, y, r, group_id): 
   
        r = constants.myround(r)
        x = constants.myround(x,4)
        y = constants.myround(y,4)
        
        (x,y) = self.screen_coords(x,y)
        colour = COLOURS[int(round(group_id))]
        self._draw_filled_circle(x, y, self.screen_radius(r), colour)

    def draw_convexhull(self,convex_hull):
        if len(convex_hull) > 0 :
            for cluster_convex in convex_hull:
                for each_convex in range(len(cluster_convex)-1):
                    self.draw_wall([cluster_convex[each_convex][0],cluster_convex[each_convex][1],cluster_convex[each_convex+1][0],cluster_convex[each_convex+1][1]])
 
              
    def draw_pedestrian_tracking(self, x, y, r, group_id,
                                 target_force_vector=(0.0,0.0),
                                 ingroup_force_vector=(0.0,0.0),
                                 outgroup_force_vector=(0.0,0.0),
                                 obstacle_force_vector =(0.0,0.0)):
        
        self.draw_pedestrian(x, y, r, group_id) 
        
        (x_target,y_target) = self.screen_coords(x+target_force_vector[0],y+target_force_vector[1])

        (x_ingroup,y_ingroup) = self.screen_coords(x+ingroup_force_vector[0],y+ingroup_force_vector[1])

        (x_outgroup,y_outgroup) = self.screen_coords(x+outgroup_force_vector[0],y+outgroup_force_vector[1])
                
        (x_obstacle,y_obstacle) = self.screen_coords(x+obstacle_force_vector[0],y+obstacle_force_vector[1])
        
        (x,y) = self.screen_coords(x,y)
        
        #draw target force                            
        self._draw_line(x, y, x_target, y_target, TARGET_FORCE__COLOUR)
        #pygame.draw.aaline(self.screen, TARGET_FORCE__COLOUR, [x, y], [x_target, y_target], True)
        
        
        #in-group force has the same color with their group
        self._draw_line(x, y, x_ingroup, y_ingroup,  COLOURS[int(round(group_id))])
        #pygame.draw.aaline(self.screen, COLOURS[int(round(group_id))], [x, y], [x_ingroup, y_ingroup], True)
                
        #out-group force has the color of the remaining group
        if int(round(group_id))==1:
            self._draw_line(x, y, x_outgroup, y_outgroup,  COLOURS[0])
            #pygame.draw.aaline(self.screen, COLOURS[0], [x, y], [x_outgroup, y_outgroup], True)
        else:
            self._draw_line(x, y, x_outgroup, y_outgroup,  COLOURS[1])
            #pygame.draw.aaline(self.screen, COLOURS[1], [x, y], [x_outgroup, y_outgroup], True)
        
        #draw wall force
        self._draw_line(x, y, x_obstacle, y_obstacle,  OBSTACLE_FORCE__COLOUR)
        #pygame.draw.aaline(self.screen, OBSTACLE_FORCE__COLOUR, [x, y], [x_obstacle, y_obstacle], True)  
        
    def draw_pedestrian_outline(self, x, y, r, group_id): 
   
        r = constants.myround(r)
        x = constants.myround(x,4)
        y = constants.myround(y,4)
        
        (x,y) = self.screen_coords(x,y)
        colour = COLOURS[int(round(group_id))]
        self._draw_circle(x, y, self.screen_radius(r), colour)
    
    def draw_target(self, x, y):
        (x,y) = self.screen_coords(x,y)
        if x > self.width or x < -self.width or y > self.height or y < -self.height:
            return
        pygame.draw.circle(self.screen, TARGET_PINK__COLOUR, (x,y), self.screen_radius(0.2), 0)

    def draw_text(self, t, draw_fps=True):
        if draw_fps:
            text = "%s - %d fps" % (t, self.clock.get_fps())
        else:
            text = t
        texture = self.font.render(text, 
                True, DRAW__DARK_COLOUR, BG_WHITE_COLOUR)
        self.screen.blit(texture, texture.get_rect())
    
    def screen_coords(self, x, y):
       
        x *= self.pixel_factor
        y *= self.pixel_factor

        shift_w = self.width/2
        shift_h = self.height/2
    
        x += shift_w
        y += shift_h
        
        return (int(x),int(y))
        
    def screen_radius(self, r):
        return int(r*self.pixel_factor)

    def convert_pos_coords(self,x,y):
        
        shift_w = self.width/2
        shift_h = self.height/2
        
        x = (x-shift_w)/self.pixel_factor
        y = (y-shift_h)/self.pixel_factor
        return (x,y)
    
    def get_pos_tracked(self):
        return self.pedestrian_pos_track
    
    
    def reset_tracked_position(self):
        self.pedestrian_pos_track =  [-999.0,-999.0]
    
        
    def is_tracked_pedestrian(self, pos_x, pos_y):

        if self.pedestrian_pos_track[0] == -999.0 and self.pedestrian_pos_track[1] == -999.0:
            return False
        elif hypot(self.pedestrian_pos_track[0]-pos_x, self.pedestrian_pos_track[1]- pos_y) < self.threshold_track_pedestrian_pos:
            return True
        
        return False   
