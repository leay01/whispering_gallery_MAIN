# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:40:45 2022

@author: mowit
"""
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np


path = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220818_NIST_Resonator_Box_Data\\Flux_Ramp_Results\\'
bins = 50

data = pd.read_table(path+'resonance_parameters_trial_0.txt',sep=',')

data['Q_e'] = data['Q_e_real']+1j*data['Q_e_imag']

data['Q_i'] = (data['Q']*data['Q_e'])/(data['Q_e']-data['Q'])

data['|Q_i|'] = np.abs(data['Q_i'])

data['BW'] = data['Resonant Freq']*10**3/data['Q']

deltaf=0
'''
for idx, row in data.iterrows():
    if idx == 0:
        continue
    else:
        data.loc[idx,'delta_f'] = 1
'''
data['delta_f'] = np.nan
for i in range(len(data)):
   
    if i == 0:
        continue
    else:
        delta_f = data['Resonant Freq'].iloc[i] - data['Resonant Freq'].iloc[i-1]
        data.at[i,'delta_f'] = delta_f
        #data.set_value(i,'delta_f',delta_f)
        #data['delta_f'].iloc[i] = deltaf

fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(nrows=2,ncols=2)

ax1.hist(data['Q'],bins)
ax1.set_xlabel('Q',fontsize=14)
ax1.set_ylabel('Number of Resonators',fontsize=14)

ax2.hist(data['delta_f'],bins,range=[0,15])
average_BW = data['BW'].mean()
ax2.axvline(x = 3*average_BW/10**3, color = 'r')
ax2.set_xlabel('$\Delta$f (MHz)',fontsize=14)
ax2.set_ylabel('Number of Resonators',fontsize=14)

ax3.hist(data['|Q_i|'],bins,range=[0,300000])
ax3.set_xlabel('$Q_i$',fontsize=14)
ax3.set_ylabel('Number of Resonators',fontsize=14)

ax4.hist(data['BW'],bins,range=[0,250])
ax4.set_xlabel('BW (kHz)',fontsize=14)
ax4.set_ylabel('Number of Resonators',fontsize=14)

fig.suptitle('μMUX Chip Characteristics',fontsize=16)

print(data) 

