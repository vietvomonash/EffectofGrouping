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
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
from scipy.interpolate import griddata
from mpl_toolkits.axes_grid1 import make_axes_locatable


# query by value k1 = df.loc[(df.Product == p_id) & (df.Time >= start_time) & (df.Time < end_time), ['Time', 'Product']]
# df[(df.Product == p_id) & (df.Time> start_time) & (df.Time < end_time)][['Time','Product']]
# df[df['Year'] < 2014][df['Color' == 'Red']
# df[df['Year'] < 2014][df['Color' == 'Red'][['Product','Color']]

csv.field_size_limit(500 * 1024 * 1024)
constants = [1.4, 1.6, 1.8, 2.0]
r_strength = [34.0, 36.0, 38.0, 40.0]
a_strength = [16.0, 18.0, 20.0, 24.0]  
scenarios = [1, 2]

labels = ['$c=1.4$', '$c=1.6$', '$c=1.8$', '$c=2.0$']
column_name = ['r', 'a', 'c', 'scenario', 'diff']

df = pd.read_csv("final_angle_distance.csv", header=None, names=column_name)
                
# r = df['r'].values
# a = df['a'].values
# c = df['c'].values
diff = df['diff'].values
max_diff = np.max(diff)
min_diff = np.min(diff)

for c_value in constants:
    fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(13, 5))
    for scenario, ax in zip(scenarios, axes.flat):  # in range(len(constants)):
        
        diff_same_c_scenario = []
        for i in range(len(a_strength)):
            diff_same_a = []
            for j in range(len(r_strength)):
                r_value = r_strength[j]
                a_value = a_strength[len(a_strength) - i - 1]
                different = df[(df[column_name[0]] <= r_value + .01) & (df[column_name[0]] >= r_value - .01) & 
                                (df[column_name[1]] <= a_value + .01) & (df[column_name[1]] >= a_value - .01) & 
                                (df[column_name[2]] <= c_value + .01) & (df[column_name[2]] >= c_value - .01) & 
                                (df[column_name[3]] == scenario) ].ix[:, column_name[4]].values[0]
                diff_same_a.append(different)
            diff_same_c_scenario.append(diff_same_a)
        diff_same_c_scenario = np.array(diff_same_c_scenario)


        im = ax.imshow(diff_same_c_scenario, interpolation='none', cmap='jet', vmin=min_diff, vmax=max_diff)  # , extent=[34.0, 42.0, 16.0, 24.0]) axes[c_index]
        ax.xaxis.set_ticks_position('none')    
        ax.yaxis.set_ticks_position('none')    
        ax.set_title("$Scenario\/" + str(scenario) + "$",size=16)    
        ax.set_xticklabels(['', '$R=34$', '', '$R=36$', '', '$R=38$', '', '$R=40$'])
        ax.set_yticklabels(['', '$A=24$', '', '$A=20$', '', '$A=18$', '', '$A=16$'])
        plt.subplots_adjust(wspace=0.5)        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(im, cax=cax)
        
        cbar.set_label('$Kullback–Leibler\/Distance$', size=14)    
    fig.tight_layout()
    fig.suptitle('$c=' + str(c_value) + '$', fontsize=20, position=(0.5, 1.0))
    plt.show()
