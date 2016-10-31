'''
Created on 10 Mar 2016

@author: quangv
'''

import numpy as np
import math as m
from scipy.spatial import distance
from scipy.spatial import ConvexHull
import operator
from matplotlib.path import Path
from sklearn.cluster import DBSCAN
import collections

#import matplotlib.pyplot as plt
#from scipy.cluster.hierarchy import dendrogram, linkage


def _purity_measurement(crowd):
    #crowd is a list of [x1,y1,ped_id,groupId, velocity]
    #pre-process to sort by id and compute distance matrix
    crowd =  sorted(crowd,key = lambda by_member_id: by_member_id[2])           
    crowd_coordinate = []
    for i in range(len(crowd)):
        crowd_coordinate.append((crowd[i][0],crowd[i][1]))
        
    db = DBSCAN(eps = 0.6*6,min_samples=2).fit(crowd_coordinate) #,
    labels = db.labels_
    cluster_num = set(labels)
    
    if -1 in labels:
        cluster_info = [[] for i in range(len(cluster_num)-1)] #exclude outlier -1
    else:
        cluster_info = [[] for i in range(len(cluster_num))]
    
    #since we have 2 groups, 0: black group, 1: red group
    velocity = [[] for i in range(2)]
    
    # add pedestrians to each cluster  
    for member in range(len(crowd)):
        if labels[member] !=-1:
            cluster_info[labels[member]].append(crowd[member])
            velocity[int(crowd[member][3])].append(crowd[member][4])
            
    #measure purity
    purity_cluster = []
    
    for cluster_index in range(len(cluster_info)):
        #find groupID of each pedestrian
        cluster_mem_id = [item[3] for item in cluster_info[cluster_index]]
        counter=collections.Counter(cluster_mem_id)
        dominant = 0
        for k,v in counter.items():
            if dominant < v:
                    dominant = v
                    
        purity_cluster.append(dominant)
    
    purity_measurement = np.sum(purity_cluster)/float(len(crowd))
    
    
    #compute average speed of each group
    average_velocity = []
    for velocity_element in velocity:
        average_velocity.append(np.mean(velocity_element))
        
    return purity_measurement,average_velocity  


def _DBscan(crowd):
    #crowd is a list of [x1,y1,ped_id,groupId]
    #pre-process to sort by id and compute distance matrix
    crowd =  sorted(crowd,key = lambda by_member_id: by_member_id[2])           
    crowd_coordinate = []
    for i in range(len(crowd)):
        crowd_coordinate.append((crowd[i][0],crowd[i][1]))
        
    db = DBSCAN(eps = 0.6*6,min_samples=2).fit(crowd_coordinate) #,
    labels = db.labels_
    cluster_num = set(labels)
    
    if -1 in labels:
        cluster_info = [[] for i in range(len(cluster_num)-1)] #exclude outlier -1
    else:
        cluster_info = [[] for i in range(len(cluster_num))]
        
    for member in range(len(crowd)):
        if labels[member] !=-1:
            cluster_info[labels[member]].append(crowd[member])
    
    
    hull_vertices = [[] for i in range(len(cluster_info))]
      
    for cluster_index in range(len(cluster_info)):
        temp_data = [[item[0], item[1]] for item in cluster_info[cluster_index]]
        if (len(temp_data)>=3):
            hull = ConvexHull(temp_data)
            member_array = hull.vertices
            
            for member in member_array:
                hull_vertices[cluster_index].append([temp_data[member][0],temp_data[member][1]])

    
    
    #should return the hull_vertices of each cluster
    
    return cluster_info, hull_vertices

    
def _block_kruskkal_convexhull_detection(crowd):
    #crowd is a list of [x1,y1,ped_id,groupId]
    #pre-process to sort by id and compute distance matrix
    crowd =  sorted(crowd,key = lambda by_member_id: by_member_id[2])           
    crowd_coordinate = []
    
    black_group = []
    black_coordinate = []
   
    red_group = []
    red_coordinate = []
 
    for i in range(len(crowd)):
        crowd_coordinate.append((crowd[i][0],crowd[i][1]))
        if crowd[i][3]== 0:
            black_group.append(crowd[i])
            black_coordinate.append((crowd[i][0],crowd[i][1]))
        else:
            red_group.append(crowd[i])    
            red_coordinate.append((crowd[i][0],crowd[i][1]))

               
    crowd_coordinate = np.array(crowd_coordinate)
   
    if len(black_group) > 2:
        black_coordinate = np.array(black_coordinate)
        black_distance_matrix = distance.squareform(distance.pdist(black_coordinate))
        #structure graph . [(ped1,ped2,weight), (),...]
        black_graph = _generate_graph(black_group,black_distance_matrix)
    
    if len(red_group) > 2 :
        red_coordinate = np.array(red_coordinate)
        red_distance_matrix = distance.squareform(distance.pdist(red_coordinate))
        red_graph = _generate_graph(red_group,red_distance_matrix)
    
    
    black_blocks = []
    red_blocks = []
    
    print("===========")
    if len(black_group) > 2:
        black_blocks = _blocks_of_group_detection(crowd, black_group,black_graph, red_group)       
        print(black_blocks)
    if len(red_group) > 2 :
        red_blocks = _blocks_of_group_detection(crowd, red_group,red_graph, black_group)
        print(red_blocks)
    
    hull_vertices = [[] for i in range(len(black_blocks) + len(red_blocks))]
    index = 0
    for black_block in  black_blocks:
        temp_data = []
        for member in black_block:
            ped = crowd[int(member)]
            temp_data.append([ped[0], ped[1]])
        hull = ConvexHull(temp_data)
        member_array = hull.vertices
        for member in member_array:
            hull_vertices[index].append([temp_data[member][0],temp_data[member][1]])
        
        index+=1
        
    for red_block in  red_blocks:
        temp_data = []
        for member in red_block:
            ped = crowd[int(member)]
            temp_data.append([ped[0], ped[1]])
        if len(temp_data) >=3:   
            hull = ConvexHull(temp_data)
            member_array = hull.vertices
            for member in member_array:
                hull_vertices[index].append([temp_data[member][0],temp_data[member][1]])
        
        index+=1    
    
    return hull_vertices
    #return black_blocks,red_blocks
    
def _generate_graph(group, group_distance_matrix):
    
    graph = {}
    for member_index in range(len(group)):
        for member_j_index in range(member_index+1, len(group)):
            graph[(int(group[member_index][2]),int(group[member_j_index][2]))] = group_distance_matrix[member_index][member_j_index]
        
    graph = [(ped1,ped2,weight) for (ped1,ped2),weight in graph.items() ]
    graph.sort(key=operator.itemgetter(2))
    return graph

def _blocks_of_group_detection(crowd, group_ped, group_graph, out_group_list):

    #group_graph structure: [(ped1,ped2,weight), (),...]
    #out_group_list structure: [(x,y,ped_id,groupId),(x,y,ped_id,groupId),(x,y,ped_id,groupId)]
    
    #block structure = [[ped_id,ped_id,...],[ped_id,ped_id,...]]
    blocks = []
    #should write all hull_path

    while(len(group_graph)) > 0:
        ped_start = group_graph[0][0]
        ped_end = group_graph[0][1]
            
        block_start = [ped_start]
        block_end =  [ped_end]
            
        '''find the block(cloud) that already contains ped_start, and for ped_end as wel'''
        block_index_start = _find_block_exist(blocks,ped_start)
        block_index_end = _find_block_exist(blocks,ped_end)
            
        if  block_index_start != -1:
            block_start = blocks[block_index_start]   
            
        if block_index_end !=-1:
            block_end = blocks[block_index_end]
        if block_start !=block_end:
            
            '''find convex hull of this merging blocks '''
            temp_cloud =  block_start + block_end
            temp_cloud_coordinate = [[crowd[item][0],crowd[item][1]] for item in temp_cloud]
            temp_cloud_coordinate = np.array(temp_cloud_coordinate)
            
            check_inside = True
            if len(temp_cloud_coordinate) > 2:
                temp_hull = ConvexHull(temp_cloud_coordinate)
                hull_path = Path( temp_cloud_coordinate[temp_hull.vertices])   
                
                '''check whether or not this hull path contains any out_of_group pedestrians'''
                check_inside =  check_inside_convex_hull(hull_path,out_group_list)
                
            if check_inside == False or  len(temp_cloud_coordinate) == 2:
                '''remove block_start, block_end from blocks'''
                try:
                    blocks.remove(block_start)
                except:
                    pass
                
                try:
                    blocks.remove(block_end)
                except:
                    pass
                
                '''union these cloud'''
                blocks.append(temp_cloud)
                                
            '''break any edge between C1 and  C2 in graph'''
            removeable = []
            
            for member_start in block_start:
                for member_end in block_end:

                    for edge_index in range(len(group_graph)):
                        if (group_graph[edge_index][0] == member_start and group_graph[edge_index][1]== member_end) or (group_graph[edge_index][0] == member_end  and group_graph[edge_index][1]== member_start):
                                removeable.append(group_graph[edge_index])

            
            for item in removeable:
                try:
                    group_graph.remove(item)
                except:
                    pass
        
        
    ''' points are not belong to any blocks should is at outlier'''
    for member in group_ped:
        is_existed = _find_block_exist(blocks, int(member[2]))           
        if is_existed==-1:
            blocks.append([int(member[2])])
    
    return blocks
    
def _find_block_exist(blocks, ped_start):

    for block_index in range(len(blocks)):
        if ped_start in blocks[block_index]:
            return block_index
    
    return -1

def check_inside_convex_hull(hull_path, out_group_list):
    
    for out_group_member in out_group_list:
        if hull_path.contains_point((out_group_member[0],out_group_member[1])) == True:
            return True
    
    return False
          
          
def _block_detection(crowd, max_num_per_group):
    #crowd is a list of [x1,y1,ped_id,groupId]
    
    #pre-process to sort by id and compute distance matrix
    crowd =  sorted(crowd,key = lambda by_member_id: by_member_id[2])           
    crowd_coordinate = []
    for i in range(len(crowd)):
        crowd_coordinate.append((crowd[i][0],crowd[i][1]))
            
    crowd_coordinate = np.array(crowd_coordinate)
    distance_matrix = distance.squareform(distance.pdist(crowd_coordinate))
    
    final_block = [[] for f in range(len(max_num_per_group))]
    
    for giving_ped in crowd:
        
        group_id = int(giving_ped[3])
        surrounding_list = surrounding_same_group_detection(crowd,distance_matrix,giving_ped, max_num_per_group[group_id])
        block_index_of_neighbor = []
        
        for member in surrounding_list:
            block_index_neighbor = find_block_contain_giving_ped(member,final_block[group_id])
            if block_index_neighbor !=-1 and block_index_neighbor not in block_index_of_neighbor:
                block_index_of_neighbor.append(block_index_neighbor)
        
        if len(block_index_of_neighbor) == 0:
            final_block[group_id].append(surrounding_list) 
        else:
            block_of_neighbor = []
            temp = []
            for block_index_neighbor in block_index_of_neighbor:
                in_original = set(block_of_neighbor) 
                in_neighbor = final_block[group_id][block_index_neighbor]
                temp.append(in_neighbor)
                in_second = set(in_neighbor)
                in_second_but_not_in_first = in_second - in_original
                block_of_neighbor = block_of_neighbor + list(in_second_but_not_in_first)
                
            for item in temp:
                try:
                    final_block[group_id].remove(item)
                except:
                    pass
                
            final_block[group_id].append(block_of_neighbor) 
        
    return final_block


def surrounding_same_group_detection(crowd, distance_matrix, giving_ped, MAX):            
    #algorithm to find neighbors who are belong to the same group of this given members
    # MAX population size of this group
    
    X1 = [giving_ped] #for final list
    X2 = [] # for list of visited points which are in different group from current given ped 
    
    stop_condition = False
    visited = [0] * len(crowd)
    
    #this current giving ped is already visited
    visited[int(giving_ped[2])]= 1 
    i = 0
    while i <MAX and not stop_condition:
        candidate_list = []
        X1_id = [item[2] for item in X1]
        
        #each member in X1 is used to find one nearest only, unvisited and make sure there is no other member in X closer than
        for index in range(len(X1)):
            current_point = X1[index]
                
            unvisited_list = [item for item in range(len(visited)) if visited[item] == 0]
            if len(unvisited_list)> 0:
                nearest_neighbor = unvisited_list[0]
                min_distance = distance_matrix[current_point[2]][nearest_neighbor]
                    
                for temp in range(len(unvisited_list)):  
                    temp_distance = distance_matrix[current_point[2]][unvisited_list[temp]]
                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        nearest_neighbor = unvisited_list[temp]
                
                #make sure that this distance is shortest among other member in X
                is_shortest = True
                for member in X1:
                    temp_distance = distance_matrix[member[2]][nearest_neighbor]
                    if temp_distance <  min_distance:
                        is_shortest = False
                        
                #only add into candidate if shortest is True
                if is_shortest==True and nearest_neighbor not in candidate_list:
                    candidate_list.append(nearest_neighbor)
                    visited[nearest_neighbor] = 1 
                
        if len(candidate_list) == 0:
            stop_condition = True
        else:
            removeable_candidates = []
            for nearest_neighbor in candidate_list:
                check = False
                                
                """if this point is the nearest of anyone inside X1, we add into the candidate list"""  
                for same_group in X1:
                    distance_of_same_group = distance_matrix[same_group[2]]
                    same_group_check = min(enumerate(distance_of_same_group), key=lambda x: x[1] if x[1] > 0 else float('inf'))
                    if same_group_check[0] == nearest_neighbor:
                        check = True
                    
                """ if nearest of this candidate is inside X1"""
                distance_list_check = distance_matrix[nearest_neighbor]
                nearest_neighbor_check = min(enumerate(distance_list_check), key=lambda x: x[1] if x[1] > 0 else float('inf'))
                                    
                inside_X1 = [item for item in X1 if item[2] == nearest_neighbor_check[0]]
                if len(inside_X1) > 0: # it exist
                    check = True
                
                if check== False:                                                                       
                    if len(X1) > 1:
                        """compute the shortest distance between this nearest_neighbor and a member in X1"""
                        min_temp_distance = np.sqrt( (X1[0][0] - crowd[nearest_neighbor][0])**2 + (X1[0][1] - crowd[nearest_neighbor][1])**2)  
                        nearest_in_X1 = X1[0]
                        for memberX1 in X1:
                            distance_check = np.sqrt( (memberX1[0] - crowd[nearest_neighbor][0])**2 + (memberX1[1] - crowd[nearest_neighbor][1])**2)  
                            if distance_check < min_temp_distance:
                                min_temp_distance = distance_check
                                nearest_in_X1 = memberX1
                                                
                        """ if the distance 'min_temp_distance' between (current_point of X1-> this point) is less than the maximum distance of this member to any other member in X1, we add this point into list""" 
                        distance_pedestrian = distance_matrix[nearest_in_X1[2]]
                        distance_group = []
                        for distance_temp_index in range(len(distance_pedestrian)):
                            if distance_temp_index in X1_id and distance_temp_index!=nearest_in_X1[2]:
                                distance_group.append(distance_pedestrian[distance_temp_index])
                        
                        if min_temp_distance < (np.max(distance_group) + 0.3):
                            check = True
                        else:
                            check = False
                
                if check == True:
                    #find nearest point in X1 of this candidate
                    min_temp_distance = np.sqrt( (X1[0][0] - crowd[nearest_neighbor][0])**2 + (X1[0][1] - crowd[nearest_neighbor][1])**2)  
                    nearest_inside_X1 = X1[0]
                        
                    for memberX1 in X1:
                        distance_check = np.sqrt( (memberX1[0] - crowd[nearest_neighbor][0])**2 + (memberX1[1] - crowd[nearest_neighbor][1])**2)  
                        if distance_check < min_temp_distance:
                            min_temp_distance = distance_check
                            nearest_inside_X1 = memberX1
                                
                    """if min_temp_distance is greater than the nearest of (nearest_inside_X1) in X2 """   
                    for memberX2 in X2:
                        distance_to_X2 = np.sqrt( (memberX2[0] - nearest_inside_X1[0])**2 + (memberX2[1] - nearest_inside_X1[1])**2) 
                        distance_candidate_outgroup = np.sqrt( (memberX2[0] - crowd[nearest_neighbor][0])**2 + (memberX2[1] - crowd[nearest_neighbor][1])**2) 
                            
                        if distance_to_X2 < min_temp_distance and (min_temp_distance > distance_candidate_outgroup + 0.3):
                            check = False
                            
                
                if check==False:
                    removeable_candidates.append(nearest_neighbor)
                    visited[nearest_neighbor] = 0
                    
            ''' remove in candidate_list'''
            for item in removeable_candidates:
                try:
                    candidate_list.remove(item)
                except:
                    pass        
            if len(candidate_list)  ==0:
                stop_condition =True
            else:
                for nearest_neighbor in candidate_list:
                    if crowd[nearest_neighbor][3] == giving_ped[3] and nearest_neighbor not in X1:
                        X1.append(crowd[nearest_neighbor])      
                    else:
                        X2.append(crowd[nearest_neighbor])
        i+=1
        
    return X1


def find_block_contain_giving_ped(giving_ped,final_block_of_group):
    matched = -1
    
    for block in range(len(final_block_of_group)):
        for ped in final_block_of_group[block]:
            if ped[2] == giving_ped[2]:              
                return block
    return matched


          
def _distance(x1, y1, r1, x2, y2, r2):
        a = m.sqrt(m.pow(x1 - x2, 2) + m.pow(y1 - y2, 2))
        a = a - (r1 + r2)
        return a



''' distance between two clusters is the distance between two nearest pedestrians who are belong two different cluster'''
''' could not use centroid distance since cluster may big size'''   
def _find_distance_between_clusters(in_group_cluster,out_group_cluster):
    
    distance = 0.0
    radii = 0.3
    if len(in_group_cluster) > 0 and len(out_group_cluster)>0:
        distance = _distance(in_group_cluster[0][0],in_group_cluster[0][1], radii, out_group_cluster[0][0], out_group_cluster[0][1],radii)
        
        for memberX1 in in_group_cluster:
            for memberX2 in out_group_cluster:
                temp_distance =  _distance(memberX1[0],memberX1[1], radii, memberX2[0], memberX2[1],radii)
                if temp_distance < distance:
                    distance = temp_distance
                    
                    
    return distance
    
    
    
#compute histogram of each pair of members
'''population_coordinate = []
            for i in range(population_number):
                (x,y) = force_model.group_pedestrian_a_property(i, "position")
                population_coordinate.append([x, y])
            
            population_coordinate = np.array(population_coordinate)
            D = distance.squareform(distance.pdist(population_coordinate))
            x = np.reshape(D, np.product(D.shape)) 
            n, bin_edges = np.histogram(x, bins = 10, normed = True)
            for i in range(len(n)):
                self.score_distribution[i] = self.score_distribution[i]  + n[i]
'''
       
def compute_cd_inside_group(self,a):
        
        comfortable_distances_within_group_py = []
        for i in range(len(a)):
            b = [[] for f in range(len(a[i]))]
            
            for k in range(len(a[i])):                
                for l in range (len(a[i])):
                    if k == l:
                        b[k].append(0)
                    else:
                        b[k].append(self._distance(a[i][k][0], a[i][k][1], a[i][k][2], a[i][l][0], a[i][l][1], a[i][l][2]))
            
            cd_inside_group = []
            for k in range(len(b)):
                temp = b[k]
                while 0 in temp: temp.remove(0)
                cd_inside_group.append(np.mean(temp))
            
            comfortable_distances_within_group_py.append(np.mean(cd_inside_group))     
               
        return comfortable_distances_within_group_py
    
def compute_cd_between_groups(self, a):
        
        cd_between_groups = []
        
        for i in range(len(a)):
            for j in range(i+1,len(a)):
                
                for ped_index in range(len(a[i])):
                    b = []
                    for ped_index2 in range(len(a[j])):
                        b.append(self._distance(a[i][ped_index][0], a[i][ped_index][1], a[i][ped_index][2],
                                                a[j][ped_index2][0], a[j][ped_index2][1], a[j][ped_index2][2]))
                    
                    
                    cd_between_groups.append(np.mean(b))                                                                                          
        
        return np.mean(cd_between_groups)        
    
'''def augmented_dendrogram(self, *args, **kwargs):

        ddata = dendrogram(*args, **kwargs)

        if not kwargs.get('no_plot', False):
            for i, d in zip(ddata['icoord'], ddata['dcoord']):
                x = 0.5 * sum(i[1:3])
                y = d[1]
                plt.plot(x, y, 'ro')
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -8),
                             textcoords='offset points',
                             va='top', ha='center')

        return ddata'''

#compute silhouette index using _compute_silhouette_index
'''
            a = [[] for i in range(len(self.parameters['group_num']))]
            group_population_number = int(force_model.get_population_size())
            for i in range(group_population_number):
                (x,y) = force_model.group_pedestrian_a_property(i, "position")
                r = force_model.group_pedestrian_a_property(i, "radius")
                group_id = force_model.group_pedestrian_a_property(i, "groupid")
                a[int(group_id)].append((x, y, r, group_id))
            
            self._compute_silhouette_index(self,a)
'''
       
def _compute_silhouette_index(self,a):
        score = []
        for i in range(len(a)):
                
                for k in range(len(a[i])):  
                    #compute average distance to its members      
                    b = []
                    for l in range (len(a[i])):
                        if k == l:
                            b.append(0)
                        else:
                            b.append(self._distance(a[i][k][0], a[i][k][1], a[i][k][2], a[i][l][0], a[i][l][1], a[i][l][2]))
            
                    while 0 in b: b.remove(0)
                    
                    average_dissimilarity_in_group = np.mean(b)
                    
                    #average dissimilarity of i to any other clusters
                    if i==0:
                        other_group_index = 1
                    else:
                        other_group_index = 0  
                    
                    b = []    
                    for ped_index in range(len(a[other_group_index])):
                        
                        b.append(self._distance(a[i][k][0], a[i][k][1], a[i][k][2],
                                                a[other_group_index][ped_index][0], a[other_group_index][ped_index][1], a[other_group_index][ped_index][2]))
                    
                    
                    average_dissimilarity_out_group =   np.mean(b)               
                    
                    silhouette = (average_dissimilarity_out_group - average_dissimilarity_in_group)/max(average_dissimilarity_in_group,average_dissimilarity_out_group)
                    score.append(silhouette)
            
        self.result = np.sum(score)

#plot hierarchical distance using compute_dendrogram      
'''
            population_coordinate = []
            label_colors = dict()
            labels_id = []
            for i in range(population_number):
                (x,y) = force_model.group_pedestrian_a_property(i, "position")
                member_id = force_model.group_pedestrian_a_property(i, "ped_id")
                group_id = force_model.group_pedestrian_a_property(i, "groupid")
                population_coordinate.append([x, y])
                labels_id.append(str(int(member_id)))
                
                if int(group_id) == 0:
                    label_colors[str(int(member_id))] = 'k'
                else:
                    label_colors[str(int(member_id))] = 'r'
            
            
            self._compute_dendrogram(population_coordinate,labels_id,label_colors)
'''
        
'''def _compute_dendrogram(self,population_coordinate,labels_id,label_colors):
        population_coordinate = np.array(population_coordinate)
        D = distance.squareform(distance.pdist(population_coordinate))
        linkage_matrix = linkage(D, "single")
        plt.clf()
        ddata = self.augmented_dendrogram(linkage_matrix, color_threshold=1,labels=labels_id)

        ax = plt.gca()
        xlbls = ax.get_xmajorticklabels()
        for lbl in xlbls:
            lbl.set_color(label_colors[lbl.get_text()])
                
        plt.show()'''
        
        
#def _plot_sample(self):
       
        #a = [[] for i in range(len(self.parameters['group_num']))]
        
        #group_population_number = int(force_model.get_population_size())
        #for i in range(group_population_number):
        #    (x,y) = force_model.group_pedestrian_a_property(i, "position")
        #    r = force_model.group_pedestrian_a_property(i, "radius")
        #    group_id = force_model.group_pedestrian_a_property(i, "groupid")
        #    a[int(group_id)].append((x, y, r, group_id))
      
        ## compute cd_distance_inside groups
        #comfortable_distances_within_group = self.compute_cd_inside_group(a) 
        #comfortable_distances_between_groups = self.compute_cd_between_groups(a)
        #self.plots._add_sample(int(self.time), comfortable_distances_within_group, comfortable_distances_between_groups)