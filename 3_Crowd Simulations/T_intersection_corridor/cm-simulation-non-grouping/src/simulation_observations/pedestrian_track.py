'''
Created on 28 Apr 2016

@author: quangv
'''

import matplotlib.pyplot as plt

class Pedestrian_Track:
    def __init__(self, min_time):
        
        self.data = []
        self.time_total = []
        
        
        self.t_values = []
        self.target_force = []
        self.ingroup_force = []
        self.outgroup_force = []
        self.obstacle_force = []
        self.velocity_x = []
        self.current_x_position = []
        
        self.ingroup_color = ''
        self.outgroup_color = ''
                
        self.fig = plt.figure()#figsize=(8,9.2)
        plt.get_current_fig_manager().window.wm_geometry("+30+100") # move the window: x,y coordination
                
        #this sub plot to show velocity over x-direction
        self.ax2 = self.fig.add_subplot(111)
        self.ax2.set_title('Tracking forces of Pedestrian Id: ' + str('...'))
        self.ax2.set_ylabel(r'force - magnitude')
        self.ax2.set_xlabel(r'x-position (m)')
        self.ax2.grid(True)
        self.ax2.set_xlim([55,180])
                                        
        self.currentTime = min_time

        """get line to update in advance of each axis """             
        plt.show(block=False)
        
        self.label = ['Target F','In of group F','Out of group F','Wall F', 'Velocity-x']

                 
    def _force_color(self, ingroup_color, outgroup_color):    
        self.ingroup_color = ingroup_color
        self.outgroup_color = outgroup_color
        
    def _addsample(self, time, targetforce, ingroup_force, outgroup_force, obstacle_force, velocity_x, current_x_position):
        
        self.t_values.append(time)
        self.target_force.append(targetforce)
        self.ingroup_force.append(ingroup_force)
        self.outgroup_force.append(outgroup_force)
        self.obstacle_force.append(obstacle_force)
        self.velocity_x.append(velocity_x)
        self.current_x_position.append(current_x_position)
        
        self.plot_force_tracking_by_x_position()
        
    def _addsample2(self, currentTime, newdata):
        
        self.time_total.append(currentTime)
        self.data.append(newdata) 
        
    def _reset(self, current_time1, ped_id):
        
        """check from beginning of data and supply for this, only re-set these variable since it is used to plot individual"""
        self.t_values.clear()
        self.target_force.clear()
        self.ingroup_force.clear()
        self.outgroup_force.clear()
        self.obstacle_force.clear()
        self.velocity_x.clear()
        self.current_x_position.clear()
        
        for time_index in range(len(self.data)):
            #this for loop is for each pedestrian at that time
            for pedestrian in self.data[time_index]:
                #[ped_id,target_force,ingroup_force,outgroup_force,obstacle_force,velocity_x,current_position]
                if pedestrian[0] == ped_id:
                    self.target_force.append(pedestrian[1])
                    self.ingroup_force.append(pedestrian[2])
                    self.outgroup_force.append(pedestrian[3])
                    self.obstacle_force.append(pedestrian[4])
                    self.velocity_x.append(pedestrian[5])
                    self.current_x_position.append(pedestrian[6])
                                

        self.ax2.cla()

        self.ax2.set_title('Tracking forces of Pedestrian Id: ' + str(ped_id))
        self.ax2.set_ylabel(r'force - magnitude')
        self.ax2.set_xlabel(r'x-position (m)')
        self.ax2.grid(True)
        self.ax2.set_xlim([55,180])       
        
        """get line to update in advance of each axis """             
        plt.show(block=False)
        

        self.legend_plot2 = False
        
        self.ingroup_color = ''
        self.outgroup_color = ''
            
                            
    def plot_force_tracking_by_x_position(self):
        if len(self.current_x_position) > 0:
            self.ax2.draw_artist(self.ax2.patch)  
            
               
            self.ax2.plot(self.current_x_position,self.target_force,'b.-',label=self.label[0])
    
            if self.ingroup_color != '':
                self.ax2.plot(self.current_x_position,self.ingroup_force,self.ingroup_color,label=self.label[1])
                self.ax2.plot(self.current_x_position,self.outgroup_force,self.outgroup_color,label=self.label[2])
            
            self.ax2.plot(self.current_x_position,self.obstacle_force,'g.-',label=self.label[3])
            self.ax2.plot(self.current_x_position,self.velocity_x,'y.-',label=self.label[4])
            

            if self.legend_plot2 ==False:
                self.ax2.legend(loc='center left', prop={'size':13},bbox_to_anchor=(0.8, 0.85) ,shadow=False)
                self.legend_plot2=True
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()