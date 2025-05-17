# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 09:32:17 2022

@author: mowit
"""
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
#import os
from identify_resonances_v2 import remove_background, linear_normalization, fit_resonances, param_histogram

def plot_single_resonance(file_names,title,out_name,trial_num,data_column):
    data = pd.read_table(file_names,sep=',')
    
    fig, ax = plt.subplots(1)    
    
    ax.plot(data['Freq (Hz)']/10**9,data[data_column])
    ax.set_xlabel('Frequeny (GHz)')
    ax.set_ylabel('|S21| (dB)')
    fig.suptitle(title)
    
    fig.savefig('.\\{}_trial_{}.png'.format(out_name,trial_num), dpi=150)       
    plt.close(fig) 
    
def plot_single_resonance_complex(file_names,title,out_name,trial_num,data_column):
    data = pd.read_table(file_names,sep=',')
    
    comp = data[data_column].to_numpy(complex)
    real = comp.real
    imag = comp.imag
    
    fig, ax = plt.subplots(1)
    
    ax.plot(real, imag)
    ax.set_xlabel('Re[S21]')
    ax.set_ylabel('Im[S21]')
    fig.suptitle(title)
    
    fig.savefig('.\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)
    plt.close(fig)
    
def plot_single_fit(file_names,title,out_name,trial_num,data_column):
    data = pd.read_table(file_names,sep=',')
    guess_comp = data['guess'].to_numpy(complex)
    fit_comp = data['fit'].to_numpy(complex)
    
    fig, ax = plt.subplots(1)
    
    ax.plot(data['Freq (Hz)']/10**9,data[data_column],'o')
    ax.plot(data['Freq (Hz)']/10**9,20*np.log10(np.abs(guess_comp)),'--')
    ax.plot(data['Freq (Hz)']/10**9,20*np.log10(np.abs(fit_comp)),'-')
    ax.ticklabel_format(useOffset=False)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
    
    fig.savefig('.\\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)
    plt.close(fig)
    
def plot_single_fit_complex(file_names,title,out_name,trial_num,data_column):
    data = pd.read_table(file_names,sep=',')
    
    measured_comp = data[data_column].to_numpy(complex)
    measured_real = measured_comp.real
    measured_imag = measured_comp.imag
    
    guess_comp = data['guess'].to_numpy(complex)
    guess_real = guess_comp.real
    guess_imag = guess_comp.imag
    
    fit_comp = data['fit'].to_numpy(complex)
    fit_real = fit_comp.real
    fit_imag = fit_comp.imag
    
    fig, ax = plt.subplots(1)
    
    ax.plot(measured_real,measured_imag,'o')
    ax.plot(guess_real,guess_imag,'--')
    ax.plot(fit_real,fit_imag,'-')
    ax.ticklabel_format(useOffset=False)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.4f'))

    fig.savefig('.\\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)
    plt.close(fig)

if __name__ == '__main__':
    path = 'G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220818_NIST_Resonator_Box_Data\\Flux_Ramp_Results\\'
    resnumber = 7
    trial = 0

    if (trial == None):
        filenames = glob.glob(path+'windowed_'+str(resnumber)+'_trial_*.txt')
        
        for i in range(len(filenames)): 
            data = pd.read_table(filenames[i],sep=',')
            
            remove_background([filenames[i]],i)
            plot_single_resonance(filenames[i],'Background Subtracted','background_subtracted',i,'Resp w/out Background (dB)')
            
            linear_normalization([filenames[i]], i)
            plot_single_resonance(filenames[i],'Normalized','normalized',i,'Normalized Resp (dB)')
            
            param_file = fit_resonances([filenames[i]], i)
            plot_single_fit(filenames[i],'Fit','fit',i,'Normalized Resp (dB)')
    else:
        filenames = path+'windowed_'+str(resnumber)+'_trial_'+str(trial)+'.txt'
        
        data = pd.read_table(filenames,sep=',')
        
        remove_background([filenames],trial)
        plot_single_resonance(filenames,'Background Subtracted','background_subtracted',trial,'Resp w/out Background (dB)')
        plot_single_resonance_complex(filenames,'Background Subtracted','background_subtracted_complex',trial,'Comp Resp w/out Background')
        
        linear_normalization([filenames], trial)
        plot_single_resonance(filenames,'Normalized','normalized',trial,'Normalized Resp (dB)')
        plot_single_resonance_complex(filenames,'Normalized','normalized_complex',trial,'Normalized Comp Resp')
        
        param_file = fit_resonances([filenames], trial)
        plot_single_fit(filenames,'Fit','fit',trial,'Normalized Resp (dB)')
        plot_single_fit_complex(filenames,'Fit','fit_complex',trial,'Normalized Comp Resp')
            
'''      
    
    
    if (trial == None):
        filenames = glob.glob(path+'windowed_'+str(resnumber)+'_trial_*.txt')
    else:
        filenames = path+'windowed_'+str(resnumber)+'_trial_'+str(trial)+'.txt'
    
    for i in range(len(filenames)):
        if (trial == None):
            data = pd.read_table(filenames[i],sep=',')
        else:
            data = pd.read_table(filenames,sep=',')
        
        print(filenames[i])
        remove_background([filenames[i]],i)
        if (trial == None):
            plot_single_resonance(filenames[i],'Background Subtracted','background_subtracted',i,'Resp w/out Background (dB)')
        else:
            plot_single_resonance(filenames,'Background Subtracted','background_subtracted',trial,'Resp w/out Background (dB)')

        linear_normalization([filenames[i]], i)
        if (trial == None):
            plot_single_resonance(filenames[i],'Normalized','normalized',i,'Normalized Resp (dB)')
        else:
            plot_single_resonance(filenames,'Normalized','normalized',trial,'Normalized Resp (dB)')
            
        
        param_file = fit_resonances([filenames[i]], i)
        if (trial == None):
            plot_single_fit(filenames[i],'Fit','fit',i,'Normalized Resp (dB)')
        else:
            plot_single_fit(filenames,'Fit','fit',trial,'Normalized Resp (dB)')
        
        #param_histogram(param_file, 30, i)
        
'''

