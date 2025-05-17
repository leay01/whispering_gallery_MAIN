# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 10:48:51 2022

na_save_data.py

Description: This script saves the data currently displayed on the NA to a .txt file.
It uses the NetworkAnalyzer class found in na_tracer.py.

Author: Matthew Withers - MW
Editors:
    
Change Log:
    
20220725 - MW - Original Script
20220726 - MW - Continued writing original script
20220730 - MW - Added complex response data collection

@author: mowit

Make sure you install pyvisa and pyvisa-py packages.
"""

# ----- [User Inputs] ---------------------------------

VNA_GPIB_Port = 'GPIB0::14::INSTR'
Measurement_Channel = 'CH1_S21_2'
Output_File_Path = 'G:\\My Drive\\Stanford\\Kuo_Lab\\AliCPT\\20240927_final_rf_check_ali_amplifiers_returned_to_correct_position\\'
Output_File_Name = 'LNA3_unbiased'#'\\S21_3_9_GHz'

# ----- [End User Inputs] -----------------------------

# ----- [Import Packages] -----------------------------

from na_tracer import NetworkAnalyzer
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np

# ----- [End Import Packages] -------------------------

# ----- [Main Program] --------------------------------

print(f'port test: {VNA_GPIB_Port}')


na = NetworkAnalyzer(VNA_GPIB_Port)
na.initialize_device(VNA_GPIB_Port)
na.choose_channel('CH1_S21_2')

freq = na.get_old_freqs()
real, imag = na.get_old_resp_complex()

print(type(real))
print(type(imag))

z_values = [real[i]+1j*imag[i] for i in range(len(real))]

outputdata = pd.DataFrame({'Freq (Hz)':freq,'Complex (decimal)':z_values})
print(outputdata)
now=dt.datetime.now()

outputfile = Output_File_Path + Output_File_Name + '_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
outputdata.to_csv(outputfile,sep=',')


print('Data recorded at: '+now.strftime('%Y-%m-%d_%H:%M:%S'))

plt.plot(freq,20*np.log10(np.abs(z_values)))
plt.title(Measurement_Channel + ' ' + now.strftime('%Y-%m-%d_%H:%M:%S'))
plt.ylim([-100,20])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Response (dB)')
plt.show()

# ----- [End Main Program] --------------------------
