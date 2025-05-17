# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 11:27:35 2022

@author: mowit
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from basic_units import radians, cos

flow = 5.17#5.18#5.2018#5.2052#5.2030#5.2018
fhigh = 5.45#5.22#5.2024#5.2058#5.2039#5.2024

data = pd.read_table('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220818_NIST_Resonator_Box_Data\\Flux_Ramp_Combined\\1.2V_all_data.txt',sep=',')
data['Freq (GHz)'] = data['Freq (Hz)']/10**9
data = data[(flow < data['Freq (GHz)']) & (data['Freq (GHz)'] < fhigh)]

comp = data['Comp Resp'].to_numpy(complex)
real = comp.real
imag = comp.imag

amplitude = 20*np.log10(np.abs(comp))
phase = np.unwrap(np.angle(comp))

fig, ax = plt.subplot_mosaic([['amp',   'comp'],
                              ['phase', 'comp']],constrained_layout=True)

ax['amp'].plot(data['Freq (GHz)'], amplitude)
ax['amp'].set_xlabel('Frequency (GHz)')
ax['amp'].set_ylabel('|S21| (dB)')
ax['amp'].ticklabel_format(useOffset=False)

ax['phase'].plot(data['Freq (GHz)'], phase)
ax['phase'].set_xlabel('Frequency (GHz)')
ax['phase'].set_ylabel('Phase (rad)')
ax['phase'].ticklabel_format(useOffset=False)

ax['comp'].plot(real,imag)
ax['comp'].set_xlabel('Re[S21]')
ax['comp'].set_ylabel('Im[S21]')
ax['comp'].ticklabel_format(useOffset=False)

fig.suptitle('Flux Ramp Line with 0 $\Phi_0$ of Flux')

plt.show()

