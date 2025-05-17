# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 15:11:00 2022

@author: mowit
"""

from na_tracer import NetworkAnalyzer
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import pyvisa

VNA_GPIB_Port = 'GPIB1::16::INSTR'
VNA_Channel = 'CH1_S21_2'

Freq_Start = 5.18240*10**9
Freq_End = 5.43674*10**9
Freq_Step = 5*10**6

na = NetworkAnalyzer(VNA_GPIB_Port)
na.initialize_device(VNA_GPIB_Port)
na.choose_channel(VNA_Channel)

windows = np.arange(Freq_Start,Freq_End+Freq_Step,Freq_Step)

for j in np.arange(0,len(windows),1):
    if j == 0:
        continue
    else:
        na.write_command(['SENS:AVER OFF\n']) 
        na.write_command(['SENS:FREQ:STAR {}'.format(windows[j-1])])
        na.write_command(['SENS:FREQ:STOP {}'.format(windows[j])]) 
        na.write_command(['SENS:AVER ON\n'])
        time.sleep(10)
        
    freq = na.get_pna_freq()
    resp = na.get_pna_response()
    compresp = na.get_pna_complex_response()

    outputdata = pd.DataFrame({'Freq (Hz)':freq,'Resp (dB)':resp,'Comp Resp':compresp})
    now=dt.datetime.now()
    
    #if j == 0:
    #    outputfile = '{}GHz_{}GHz_{}V_'.format(windows[j]/10**9,(windows[j]+Freq_Step)/10**9,i) + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
    #else:
    outputfile = '{}GHz_{}GHz_'.format(windows[j-1]/10**9,windows[j]/10**9) + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
    outputdata.to_csv(outputfile,sep=',')