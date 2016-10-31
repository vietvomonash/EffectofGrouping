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
'''
K_max = 20
K_min = 0
L_max = 20
L_min = 0
ax = plt.subplot(111)
x_offset = 7 # tune these
y_offset = 7 # tune these
plt.setp(ax, 'frame_on', False)
ax.set_ylim([0, (K_max-K_min +1)*y_offset ])
ax.set_xlim([0, (L_max - L_min+1)*x_offset])
ax.set_xticks([])
ax.set_yticks([])
ax.grid('off')

for k in np.arange(K_min, K_max + 1):
    for l in np.arange(L_min, L_max + 1):
        ax.plot(np.arange(5) + l*x_offset, 5+rand(5) + k*y_offset,
                'r-o', ms=1, mew=0, mfc='r')
        ax.plot(np.arange(5) + l*x_offset, 3+rand(5) + k*y_offset,
                'b-o', ms=1, mew=0, mfc='b')
        ax.annotate('K={},L={}'.format(k, l), (2.5+ (k)*x_offset,l*y_offset), size=3,ha='center')
plt.savefig(os.path.join(os.getcwd(), 'plot-average.pdf'))
plt.show()
print('Final plot created.')
'''

# query by value k1 = df.loc[(df.Product == p_id) & (df.Time >= start_time) & (df.Time < end_time), ['Time', 'Product']]
# df[(df.Product == p_id) & (df.Time> start_time) & (df.Time < end_time)][['Time','Product']]
# df[df['Year'] < 2014][df['Color' == 'Red']
# df[df['Year'] < 2014][df['Color' == 'Red'][['Product','Color']]

csv.field_size_limit(500 * 1024 * 1024)
constants = [1.4, 1.6, 1.8, 2.0]
r_strength = [34.0, 36.0, 38.0, 40.0]  # 44.0
a_strength = [16.0, 18.0, 20.0, 24.0] 


labels = ['$c=1.4$', '$c=1.6$', '$c=1.8$', '$c=2.0$']
column_name = ['r', 'a', 'c', 'diff', 'similar']
df = pd.read_csv("final_flowrate_mean.csv", header=None, names=column_name)
                
# r = df['r'].values
# a = df['a'].values
# c = df['c'].values
diff = df['diff'].values
max_diff = np.max(diff)
min_diff = np.min(diff)

r_set = []
a_set = []
c_set = []
diff = []


fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))  #  
# fig.suptitle('Title of figure', fontsize=20)

for c_value, ax in zip(constants, axes.flat):  # in range(len(constants)):
    diff_same_c = []
    for i in range(len(a_strength)):
        diff_same_a = []
        for j in range(len(r_strength)):
            r_value = r_strength[j]
            a_value = a_strength[len(a_strength) - i - 1]
            # c_value = constants[c_index]
            different = df[(df[column_name[0]] <= r_value + .01) & (df[column_name[0]] >= r_value - .01) & 
                            (df[column_name[1]] <= a_value + .01) & (df[column_name[1]] >= a_value - .01) & 
                            (df[column_name[2]] <= c_value + .01) & (df[column_name[2]] >= c_value - .01)].ix[:, column_name[3]].values[0]
            diff_same_a.append(different)
        diff_same_c.append(diff_same_a)
    diff_same_c = np.array(diff_same_c)

    
    # Append axes to the right of ax3, with 20% width of ax3
    # Create colorbar in the appended axes
    # Tick locations can be set with the kwarg `ticks`
    # and the format of the ticklabels with kwarg `format`
    # plot this grid based on diff_same_c
    im = ax.imshow(diff_same_c, interpolation='none', cmap='jet', vmin=min_diff, vmax=max_diff)  # , extent=[34.0, 42.0, 16.0, 24.0]) axes[c_index]
    # ax.autoscale(False)
    # ax.yaxis.set_major_locator(MultipleLocator(0.25))
    # Set locations of ticks on x-axis (at every multiple of 2)    
    # ax.xaxis.set_major_locator(MultipleLocator(0.25))
    # divider = make_axes_locatable(axes[c_index])
    # cax = divider.append_axes("right", size="20%", pad=0.05)
    # ax.xaxis.set_ticks(r_strength)  
    # ax.yaxis.set_ticks(a_strength)
    ax.xaxis.set_ticks_position('none')    
    ax.yaxis.set_ticks_position('none')    
    ax.set_title("$c=" + str(c_value) + "$", fontsize=18)    
    ax.set_xticklabels(['', '$R=34$', '', '$R=36$', '', '$R=38$', '', '$R=40$'])  # 34.0, 36.0, 38.0, 42.0]
    ax.set_yticklabels(['', '$A=24$', '', '$A=20$', '', '$A=18$', '', '$A=16$'])  # 16.0, 18.0, 22.0, 24.0
    plt.subplots_adjust(wspace=0.5)        
    # axes[c_index].set_xticks(r_strength)
    # axes[c_index].set_yticks(a_strength)    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    # cax = fig.add_axes([0.91, 0.1, 0.03, 0.8])
    # fig.colorbar(im,fraction=0.046, pad=0.04)
    cbar = fig.colorbar(im, cax=cax)
	
    cbar.set_label('$\Delta_{Flow\/rate}$', size=18)    
fig.tight_layout()
plt.show() 
