'''
Created on 26 Apr 2016

@author: quangv
'''
import json

class Track_Pedestrian(object):
    
    def __init__(self, pedestrian_id, group_id, radius, position):
        self.ped_id = pedestrian_id
        self.group_id = group_id
        self.radius = radius
        self.position = position
        
    def get_ped_id(self):
        return self.ped_id
    def set_ped_id(self, value):
        self.ped_id = value

    def get_group_id(self):
        return self.group_id
    def set_group_id(self, value):
        self.group_id = value
        
    def get_radius(self):
        return self.radius
    def set_radius(self, value):
        self.radius = value
        
    def get_position(self):
        return self.position
    def set_position(self, value):
        self.position = value
    