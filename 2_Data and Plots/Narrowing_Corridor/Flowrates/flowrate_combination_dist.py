import brewer2mpl
import glob, os
import csv
import matplotlib.pyplot as plt
from pylab import *
import datetime
import numpy as np
from scipy import stats
import pandas as pd
from itertools import islice
from sklearn.preprocessing import StandardScaler
from matplotlib import cm
from matplotlib import rcParams

# query by value k1 = df.loc[(df.Product == p_id) & (df.Time >= start_time) & (df.Time < end_time), ['Time', 'Product']]
# df[(df.Product == p_id) & (df.Time> start_time) & (df.Time < end_time)][['Time','Product']]
# df[df['Year'] < 2014][df['Color' == 'Red']
# df[df['Year'] < 2014][df['Color' == 'Red'][['Product','Color']]

csv.field_size_limit(500 * 1024 * 1024)
constants = [1.4, 1.6, 1.8, 2.0]
r_strength = [34.0, 36.0, 38.0, 42.0] 
a_strength = [16.0, 18.0, 22.0, 24.0] 
labels = ['$c=1.4$', '$c=1.6$', '$c=1.8$', '$c=2.0$']
column_name = ['r', 'a', 'c', 'scenario', 'flowrates']
df = pd.read_csv("final_flowrate_distribution.csv", header=None, names=column_name)
set1 = brewer2mpl.get_map('Set1', 'qualitative', 7).mpl_colors
                
fig, axes = plt.subplots(nrows=4, ncols=4, sharex=True, sharey=True, figsize=(12, 12))
for i, row in enumerate(axes):
    for j, cell in enumerate(row):
        
        # i specifies for A
        # j specifies for R
        r_value = r_strength[j]
        a_value = a_strength[len(a_strength) - 1 - i]
        
        flowrates = [[[], []] for s in range(4)]
        for c_index in range(len(constants)):
            c_value = constants[c_index]
            
            flowrate_s1 = df[(df[column_name[0]] <= r_value + .01) & (df[column_name[0]] >= r_value - .01) & 
                            (df[column_name[1]] <= a_value + .01) & (df[column_name[1]] >= a_value - .01) & 
                            (df[column_name[2]] <= c_value + .01) & (df[column_name[2]] >= c_value - .01) & 
                            (df[column_name[3]] == 1)].ix[:, column_name[4]].values[0]
            flowrates[c_index][0] = eval(flowrate_s1)
            
            flowrate_s2 = df[(df[column_name[0]] <= r_value + .01) & (df[column_name[0]] >= r_value - .01) & 
                            (df[column_name[1]] <= a_value + .01) & (df[column_name[1]] >= a_value - .01) & 
                            (df[column_name[2]] <= c_value + .01) & (df[column_name[2]] >= c_value - .01) & 
                            (df[column_name[3]] == 2)].ix[:, column_name[4]].values[0]
            flowrates[c_index][1] = eval(flowrate_s2)
        
        for c_index in range(len(constants)):
            c_value = constants[c_index]
            flowrate_pair = flowrates[c_index]
            position1 = (c_index * 1.9) + 1
            position2 = position1 + 0.6
            bp1 = cell.boxplot(flowrate_pair, positions=[position1, position2], widths=0.3)
            
            plt.setp(bp1['boxes'][0], color=set1[1])
            plt.setp(bp1['caps'][0], color=set1[1])
            plt.setp(bp1['caps'][1], color=set1[1])
            plt.setp(bp1['whiskers'][0], color=set1[1])
            plt.setp(bp1['whiskers'][1], color=set1[1])
            plt.setp(bp1['medians'][0], color=set1[0])
            
            plt.setp(bp1['boxes'][1], color=set1[3])
            plt.setp(bp1['caps'][2], color=set1[3])
            plt.setp(bp1['caps'][3], color=set1[3])
            plt.setp(bp1['whiskers'][2], color=set1[3])
            plt.setp(bp1['whiskers'][3], color=set1[3])
            plt.setp(bp1['medians'][1], color=set1[0])

        cell.spines['top'].set_visible(False)
        cell.spines['right'].set_visible(False)
        cell.spines['bottom'].set_visible(False)
            
        cell.set_title('$R=' + str(r_value) + '\/A=' + str(a_value) + '$')
        cell.axis('on')
        cell.xaxis.set_ticks_position('none')
        cell.yaxis.set_ticks_position('none')
        cell.set_xticklabels(labels)         
        # cell.xaxis.set_ticks([1.4, 1.6, 1.8, 2.0])      
        cell.set_xticks([1.5, 3.5, 5.5, 7.5])
        formatter = ScalarFormatter(useOffset=False)
        cell.yaxis.set_major_formatter(formatter)
        cell.set_xlim(0.5, 8)
        cell.grid(True)    
        if i == len(axes) - 1:
            cell.set_xlabel("$R=" + str(r_strength[j]) + "$", fontsize=18)
        if j == 0:
            cell.set_ylabel("$A=" + str(a_strength[len(a_strength) - 1 - i]) + "$", fontsize=18)
            


fig.tight_layout()  # Or equivalently,  "plt.tight_layout()"
# axes[0, 0].set_title('Axis [0,0]')
# axarr[0,1].axis('off')
plt.setp([a.get_xticklabels() for a in axes[0, :]], visible=True)
plt.setp([a.get_xticklabels() for a in axes[1, :]], visible=True)
plt.setp([a.get_xticklabels() for a in axes[2, :]], visible=True)
plt.setp([a.get_xticklabels() for a in axes[3, :]], visible=True)
# plt.setp([a.get_yticklabels() for a in axes[:, 1]], visible=True)
# fig.text(0.5, 0.04, 'common X', ha='center')
# fig.text(0.04, 0.5, 'common Y', va='center', rotation='vertical')

plt.show()
