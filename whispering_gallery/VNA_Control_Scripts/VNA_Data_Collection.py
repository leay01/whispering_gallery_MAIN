# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 16:15:34 2022

@author: mowit
"""

from modified_manualVC import modified_manualVC
from na_tracer import NetworkAnalyzer
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import pyvisa

def writeV(Adr,Channel,Volt):
    rm = pyvisa.ResourceManager()
    PS = rm.open_resource(Adr)
    if Channel == 1: Channel = 'P6V'
    if Channel == 2: Channel = 'P25V'
    if Channel == 3: Channel = 'N25V'
    PS.write('INST:SEL ' + str(Channel))
    PS.write('VOLT ' + str(Volt))
    V = PS.query('MEAS:VOLT?') 
    return(Volt,V)

PS_GPIB_Port = 'GPIB0::7::INSTR'
PS_Channel = 1
VNA_GPIB_Port = 'GPIB1::16::INSTR'
VNA_Channel = 'CH1_S21_2'

Voltage_Start = 4.5
Voltage_End = 5
Voltage_Step = 0.1 

Freq_Start = 5.18240*10**9
Freq_End = 5.43674*10**9
Freq_Step = 5*10**6


power_supply = modified_manualVC(PS_GPIB_Port)
na = NetworkAnalyzer(VNA_GPIB_Port)
na.initialize_device(VNA_GPIB_Port)
na.choose_channel(VNA_Channel)

volts = np.arange(Voltage_Start,Voltage_End+Voltage_Step,Voltage_Step)
windows = np.arange(Freq_Start,Freq_End+Freq_Step,Freq_Step)


for i in volts:
    print('V = {}'.format(i))
    
    writeV(PS_GPIB_Port,PS_Channel,i)
    
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
        outputfile = '{}GHz_{}GHz_{}V_'.format(windows[j-1]/10**9,windows[j]/10**9,round(i,1)) + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        outputdata.to_csv(outputfile,sep=',')
        
        plt.plot(freq,resp)
    
for i in np.flip(volts):
    print("Ramping voltage down")
    writeV(PS_GPIB_Port,PS_Channel,i)
    time.sleep(1)





#####

'''
for j in np.arange(0,len(windows),1):
    if j == 0:
        continue
        #na.write_command(['SENS:FREQ:STAR {}'.format(windows[j])])
        #na.write_command(['SENS:FREQ:STOP {}'.format(windows[j]+Freq_Step)])                  
        #starter = 1
    else:
        na.write_command(['SENS:FREQ:STAR {}'.format(windows[j-1])])
        na.write_command(['SENS:FREQ:STOP {}'.format(windows[j])]) 
        time.sleep(10)

    for i in volts:
       
        print('V = {}'.format(i))
        
        na.write_command(['SENS:AVER OFF\n'])    
        writeV(PS_GPIB_Port,2,i)
        na.write_command(['SENS:AVER ON\n'])
        
        #power_supply.set_volt(setV_c2=i)
        #power_supply.get_voltage()
        time.sleep(10)
        
        
        
        freq = na.get_pna_freq()
        resp = na.get_pna_response()
        compresp = na.get_pna_complex_response()
    
        outputdata = pd.DataFrame({'Freq (Hz)':freq,'Resp (dB)':resp,'Comp Resp':compresp})
        now=dt.datetime.now()
        
        #if j == 0:
        #    outputfile = '{}GHz_{}GHz_{}V_'.format(windows[j]/10**9,(windows[j]+Freq_Step)/10**9,i) + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        #else:
        outputfile = '{}GHz_{}GHz_{}V_'.format(windows[j-1]/10**9,windows[j]/10**9,i) + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        outputdata.to_csv(outputfile,sep=',')
        
        plt.plot(freq,resp)
        
    for i in np.flip(volts):
        print("Ramping voltage down")
        writeV(PS_GPIB_Port,2,i)
        time.sleep(1)
'''        
    
    
 
