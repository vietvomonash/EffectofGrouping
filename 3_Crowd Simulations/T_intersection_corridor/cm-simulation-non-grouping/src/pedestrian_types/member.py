'''
Created on 31 Mar 2015

@author: quangv
'''

import json

class Member(object):
    def __init__(self, parameters= {}):
        self.parameters = parameters
     
        self.reset_member_distribution()

    def get_out_group_r_range(self):
        return self.out_group_r_range
    def set_out_group_r_range(self, value):
        self.out_group_r_range = value


    def get_out_group_r_strength(self):
        return self.out_group_r_strength
    def set_out_group_r_strength(self, value):
        self.out_group_r_strength = value


    def get_out_group_a_range(self):
        return self.out_group_a_range
    def set_out_group_a_range(self, value):
        self.out_group_a_range = value


    def get_out_group_a_strength(self):
        return self.out_group_a_strength
    def set_out_group_a_strength(self, value):
        self.out_group_a_strength = value


    def get_in_group_r_range(self):
        return self.in_group_r_range
    def set_in_group_r_range(self, value):
        self.in_group_r_range = value


    def get_in_group_r_strength(self):
        return self.in_group_r_strength
    def set_in_group_r_strength(self, value):
        self.in_group_r_strength = value


    def get_in_group_a_range(self):
        return self.in_group_a_range
    def set_in_group_a_range(self, value):
        self.in_group_a_range = value


    def get_in_group_a_strength(self):
        return self.in_group_a_strength
    def set_in_group_a_strength(self, value):
        self.in_group_a_strength = value

    def get_target_a_strength(self):
        return self.target_a_strength
    def set_target_a_strength(self,value):
        self.target_a_strength = value
        
        
    def get_target_a_range(self):
        return self.target_a_range
    def set_target_a_range(self,value):
        self.target_a_range = value
        
    
    def reset_member_distribution(self):
        
        self.in_group_a_strength = []
        self.in_group_a_range =[]
        self.in_group_r_strength = []
        self.in_group_r_range =[]
        
        self.out_group_a_strength = []
        self.out_group_a_range = []     
        self.out_group_r_strength = []
        self.out_group_r_range = []
             
        self.target_a_strength = []
        self.target_a_range = []
             
    def _generate_member_distribution(self,num,
                                        in_group_a_strength, in_group_a_range,
                                        in_group_r_strength, in_group_r_range,
                                        out_group_a_strength, out_group_a_range, 
                                        out_group_r_strength, out_group_r_range,
                                        target_a_strength, target_a_range
                                    ):
        
        if num ==0:
            return
        self.reset_member_distribution()
        
        self.in_group_a_strength = [in_group_a_strength] * num  
        self.in_group_a_range = [in_group_a_range] * num
        self.in_group_r_strength = [in_group_r_strength] * num
        self.in_group_r_range = [in_group_r_range] * num
        
        self.out_group_a_strength = [out_group_a_strength] * num     
        self.out_group_a_range = [out_group_a_range] * num
        self.out_group_r_strength = [out_group_r_strength] * num
        self.out_group_r_range = [out_group_r_range] * num
        
        self.target_a_strength = [target_a_strength] * num
        self.target_a_range = [target_a_range] * num
    
    
    def _to_JSON(self):
        return  json.dumps(self, cls=MemberLog_Encoder)
   
class MemberLog_Encoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Member):
            return super(MemberLog_Encoder, self).default(obj)

        return obj.__dict__

class MemberLog_Decoder(json.JSONDecoder):
    def decode(self,json_string):
     
        default_obj = super(MemberLog_Decoder,self).decode(json_string)
         
        in_group_a_strength = []
        for value in default_obj['in_group_a_strength']:
            in_group_a_strength.append(value)
        
        in_group_a_range = []
        for value in default_obj['in_group_a_range']:
            in_group_a_range.append(value)
             
        in_group_r_strength = []
        for value in default_obj['in_group_r_strength']:
            in_group_r_strength.append(value)
        
        in_group_r_range = []
        for value in default_obj['in_group_r_range']:
            in_group_r_range.append(value)
        
        out_group_a_strength = []
        for value in default_obj['out_group_a_strength']:
            out_group_a_strength.append(value)
        
        out_group_a_range =[]
        for value in default_obj['out_group_a_range']:
            out_group_a_range.append(value)
       
                
        out_group_r_strength = []
        for value in default_obj['out_group_r_strength']:
            out_group_r_strength.append(value)
            
        out_group_r_range = []
        for value in default_obj['out_group_r_range']:
            out_group_r_range.append(value)
        
        
        target_a_strength = []
        for value in default_obj['target_a_strength']:
            target_a_strength.append(value)
        
        
        target_a_range = []
        for value in default_obj['target_a_range']:
            target_a_range.append(value)
        
        
        member_dist = Member()
        member_dist.set_in_group_a_strength(in_group_a_strength)  
        member_dist.set_in_group_a_range(in_group_a_range) 
        member_dist._set_in_group_r_strength(in_group_r_strength)
        member_dist._set_in_group_r_range(in_group_r_range)
       
        member_dist._set_out_group_a_strength(out_group_a_strength)
        member_dist._set_out_group_a_range(out_group_a_range)
        member_dist._set_out_group_r_strength(out_group_r_strength)
        member_dist._set_out_group_r_range(out_group_r_range)
        
        member_dist.set_target_a_strength(target_a_strength)
        member_dist.set_target_a_range(target_a_range)
        
        return member_dist