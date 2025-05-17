# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:30:23 2022

@author: mowit
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

datapath = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Flux_Ramp\\'

Voltage_Start = 0
Voltage_End = 5
Voltage_Step = 0.5

for i in np.arange(Voltage_Start,Voltage_End+Voltage_Step,Voltage_Step):
#for i in np.array([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7000000000000002,1.8,1.9000000000000001,2.0,2.1,2.2,2.3000000000000003,2.4000000000000004,2.5,2.6,2.7,2.8000000000000003,2.9000000000000004,3.0,3.1,3.2,3.3000000000000003,3.4000000000000004,3.5,3.6,3.7,3.8000000000000003,3.9000000000000004,4.0,4.1000000000000005,4.2,4.3,4.4,4.5,4.6000000000000005,4.7,4.800000000000001,4.9,5.0]):
    
    print(i)
    filenames = glob.glob(datapath+'*{}V*.txt'.format(i))
    alldata = pd.DataFrame()
    for inputfile in filenames:
        newdata = pd.read_table(inputfile,sep=',')
        alldata = pd.concat([alldata,newdata],axis=0)
    
   
    alldata.columns = ['Index','Freq (Hz)','Resp (dB)','Comp Resp']
    alldata.to_csv('.\\{}V_all_data.txt'.format(round(i,1)),index=False)
    print(alldata)
    
    #%matplotlib qt
    plt.plot(alldata['Freq (Hz)'],alldata['Resp (dB)'])
    plt.show()