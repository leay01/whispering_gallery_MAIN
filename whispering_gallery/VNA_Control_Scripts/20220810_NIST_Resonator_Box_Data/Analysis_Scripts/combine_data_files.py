# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:30:23 2022

@author: mowit
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

datapath = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\TES_Bias\\'

Voltage_Start = 0
Voltage_End = 5
Voltage_Step = 0.5

for i in np.arange(Voltage_Start,Voltage_End+Voltage_Step,Voltage_Step):
    
    filenames = glob.glob(datapath+'*{}V*.txt'.format(i))
    alldata = pd.DataFrame()
    for inputfile in filenames:
        newdata = pd.read_table(inputfile,sep=',')
        alldata = pd.concat([alldata,newdata],axis=0)
    
   
    alldata.columns = ['Index','Freq (Hz)','Resp (dB)','Comp Resp']
    alldata.to_csv('.\\{}V_all_data.txt'.format(i),index=False)
    print(alldata)
    
    #%matplotlib qt
    plt.plot(alldata['Freq (Hz)'],alldata['Resp (dB)'])
    