# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 10:17:09 2022

@author: mowit
"""

import matplotlib.pyplot as plt
import pandas as pd
#import numpy as np

path = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\' 
datafile = 'S21_LNA5_Biased_2022-08-19_095951.txt'
backgroundfile = 'S21_4_8_GHz_Background_2022-08-20_151613.txt'

data = pd.read_table(path+datafile,sep=',')
background = pd.read_table(path+backgroundfile,sep=',')

data['Resp (dB)'] = data['Resp (dB)'].astype(float)
data['Comp Resp'] = data['Comp Resp'].astype(complex)
background['Resp (dB)'] = background['Resp (dB)'].astype(float)
background['Comp Resp'] = background['Comp Resp'].astype(complex)

print(type(data['Resp (dB)'].iloc[0]))
print(type(data['Comp Resp'].iloc[0]))

data['Cal Resp (dB)'] = data['Resp (dB)']-background['Resp (dB)']
data['Cal Comp Resp'] = data['Comp Resp']-background['Comp Resp']

data.to_csv(path+'Calibrated_'+datafile)

fig, ax = plt.subplots(1)

ax.plot(data['Freq (Hz)']/10**9,data['Cal Resp (dB)'])
ax.set_ylim([-100,0])
ax.set_ylabel('|S21| (dB)')
ax.set_xlabel('Frequency (GHz)')
fig.suptitle('LNA4 - Unbiased')
plt.show()