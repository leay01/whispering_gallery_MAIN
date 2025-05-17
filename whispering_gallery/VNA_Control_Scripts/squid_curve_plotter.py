# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 17:36:20 2022

@author: mowit
"""

import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np

path = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220818_NIST_Resonator_Box_Data\\Flux_Ramp_Results\\'
datafiles = glob.glob(path+'resonance_parameters_trial_*.txt')

resfreq = pd.DataFrame({'Voltage':np.arange(0,5.1,0.1),'Freq (MHz)':np.nan})

for i in range(len(datafiles)):
    data = pd.read_table(datafiles[i],sep=',')
    resfreq.at[i,'Freq (MHz)'] = data['Resonant Freq'].iloc[4]

resfreq['Freq (GHz)'] = resfreq['Freq (MHz)']/10**3
print(resfreq)

fig, ax = plt.subplots(1)
ax2 = ax.twiny()




ax.plot(resfreq['Voltage'],resfreq['Freq (GHz)'],'o')
ax.set_ylabel('Frequency (GHz)',fontsize=14)
ax.set_xlabel('Applied Voltage (V)',fontsize=14)
ax.ticklabel_format(useOffset=False)


L = 13.3*10**-12
R = 6.44*10**3
fluxquantum = 2.068*10**-15
ax2.set_xlabel('Magnetic Flux (Φ/$Φ_0$)',fontsize=14)
ax2.ticklabel_format(useOffset=False)
ax2.set_xticks(ax.get_xticks() )
ax2.set_xbound(ax.get_xbound())
ax2.set_xticklabels([round(((x*L)/R)/fluxquantum,2) for x in ax.get_xticks()])
ax2.axvline(x=fluxquantum*R/L)
ax2.axvline(x=2*fluxquantum*R/L)
ax2.axvline(x=3*fluxquantum*R/L)
ax2.axvline(x=4*fluxquantum*R/L)
ax2.axvline(x=5*fluxquantum*R/L)

fig.suptitle('SQUID Curve of Resonance at {} GHz'.format(round(resfreq['Freq (GHz)'].iloc[0],5)),fontsize=16)

plt.show()

