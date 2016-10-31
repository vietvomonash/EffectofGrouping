import networkx as nx
import matplotlib.pyplot as plt
from influential import Influential_Member
from influential import Influential_Member_Decoder
from collections import Counter
import sys
import os, math, json
import numpy as np
from networkx.drawing.nx_agraph import graphviz_layout
import random
random.seed("Influential_network1")

influential_member_file = open("grouping_behaviour.json")
json_str = influential_member_file.read()
influential_obj=  json.loads(json_str, cls =Influential_Member_Decoder)
influential_member_file.close()
influential_member_matrix =influential_obj._get_influential()
G=nx.Graph()

influential_degree = []

for key in sorted(influential_member_matrix):
	#this list show influential pedestrians over the time
	G.add_node(key)
	influential_list=influential_member_matrix[key]
	influential_list = sorted(influential_list)	
	
	degree = len(set(influential_list))
	influential_degree.append(degree)
	#find the most occur
	#count = Counter(influential_list)
	#ped = count.most_common(1)[0]
	#G.add_node(ped[0])
	#G.add_edge(key,ped[0])
	for element in influential_list:
		G.add_node(element)
		G.add_edge(key,element)
	

#pos=nx.spring_layout(G,k=0.19,iterations=20)
#nx.draw_networkx(G)
pos = graphviz_layout(G)
#nx.draw(G,pos)


node_size=1600
node_color='blue'
node_alpha=0.3
node_text_size=12
edge_color='black'
edge_alpha=0.3
edge_tickness=1
edge_text_pos=0.3,
text_font='sans-serif'

fig = plt.figure()
			   
#nx.draw_networkx_nodes(G,pos,node_size=node_size,alpha=node_alpha, node_color=node_color)
nx.draw(G,pos,node_size=50)
nx.draw_networkx_edges(G,pos,width=edge_tickness,alpha=edge_alpha,edge_color=edge_color)
#nx.draw_networkx_labels(G, pos,font_size=node_text_size,font_family=text_font)
							
average_degree = np.mean(influential_degree)							
plt.axis('off')
fig.suptitle('$Influence\/\/\/network$', fontsize=18)
plt.annotate('$degree=' +  str(round(average_degree,2)) +'$', xycoords='axes fraction',xy=(0.4,0.9),fontsize=18)
plt.show()

