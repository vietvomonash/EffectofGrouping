'''
Created on 30 May 2016

@author: quangv
'''
import json

class Influential_Member(object):
    
    def __init__(self,influential_member_matrix):

        self.influential_member_matrix = influential_member_matrix
    
    def _set_influential(self, influential_member_matrix):
        self.influential_member_matrix = influential_member_matrix
    
    def _get_influential(self):
        return self.influential_member_matrix  
    
class Influential_Member_Encoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Influential_Member):
            return super(Influential_Member_Encoder, self).default(obj)
        return obj.__dict__

class Influential_Member_Decoder(json.JSONDecoder):
    def decode(self,json_string):
     
        default_obj = super(Influential_Member_Decoder,self).decode(json_string)
        
        influential_member_matrix = default_obj['influential_member_matrix'] 
        influential_obj = Influential_Member(influential_member_matrix)
        return influential_obj    