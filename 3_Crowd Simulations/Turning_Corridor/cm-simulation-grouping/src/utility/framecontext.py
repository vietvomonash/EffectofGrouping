'''
Created on 26 Apr 2016

@author: quangv
'''

import json

class FrameContext(object):
    
    def __init__(self, frame_second,pedestrian_list):
        
        self.frame_second = frame_second        
        self.pedestrian_list = pedestrian_list
        
  
    def get_frame_second(self):
        return self.frame_second

    def get_pedestrian_list(self):
        return self.pedestrian_list

    def set_frame_second(self, value):
        self.frame_second = value

    def set_pedestrian_list(self, value):
        self.pedestrian_list = value
    
class FrameContextLog_Encoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, FrameContext):
            return super(FrameContextLog_Encoder, self).default(obj)
        return obj.__dict__
    
class FrameContextLog_Decoder(json.JSONDecoder):
    def decode(self,json_string):
     
        default_obj = super(FrameContextLog_Decoder,self).decode(json_string)
        
        frame_second = default_obj['frame_second']
        
        pedestrian_list = default_obj['pedestrian_list']
        
        
        framecontext = FrameContext(frame_second,pedestrian_list)
            
        return framecontext      