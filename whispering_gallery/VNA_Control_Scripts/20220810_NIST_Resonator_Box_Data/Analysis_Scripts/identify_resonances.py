# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 10:48:42 2022

@author: mowit
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import os
from sklearn.linear_model import LinearRegression
#import lmfit
from resonance_fitting import ResonatorModel
#from scipy.signal import argrelextrema
#from admit.util.peakfinder.PeakDetect import PeakDetect
from scipy.signal import find_peaks

def identify_resonances(data,depth,width):
    freq = data['Freq (Hz)'].to_numpy(float)
    resp = data['Resp (dB)'].to_numpy(float)
    
    peak_ind, _ = find_peaks(-resp,height=depth,width=width)
    #print(peak_ind)
    
    locs = pd.DataFrame({'Freq (Hz)':freq[peak_ind],'Resp (dB)':resp[peak_ind]})
    #print(locs)
    count = len(peak_ind)
    print('Found {} resonances deeper than {} dB'.format(count,-depth))
    
    return locs, count

def window_resonances(data,locs,window,trial_num):
    windowed_file_names = np.array([])
    j = 0
    for i in locs['Freq (Hz)']:
        windowed_data = data[(i-window <= data['Freq (Hz)']) & (data['Freq (Hz)'] <= i+window)]
        windowed_data.to_csv('.\\windowed_{}_trial_{}.txt'.format(j,trial_num),sep = ',',index=False)
        current_file = str(os.getcwd())+'\\windowed_{}_trial_{}.txt'.format(j,trial_num)
        windowed_file_names = np.append(windowed_file_names,[current_file])
        j+=1
        
    j-=1
    return windowed_file_names

def remove_background(file_names,trial_num):
    background_subtracted_file_names = np.array([])
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        comp_data = data['Comp Resp'].to_numpy(complex)
        
        
        mag = data['Resp (dB)'].to_numpy(float)
        mag_first_10 = mag[:10]
        mag_last_10 = mag[-10:]
        mag_background_data = np.append(mag_first_10,mag_last_10,axis=0)
        mag_background = np.average(mag_background_data)
        '''
        mag = np.abs(comp_data)        
        mag_first_10 = mag[:10]
        mag_last_10 = mag[-10:]
        mag_background_data = np.append(mag_first_10,mag_last_10,axis=0)
        mag_background = np.average(mag_background_data)
        '''
        
        phase = np.angle(comp_data)
        #print(i)
        #print(phase)
        phase_first_10 = phase[:10]
        phase_last_10 = phase[-10:]
        phase_background_data = np.append(phase_first_10,phase_last_10,axis=0)
        phase_background = np.average(phase_background_data)
        
        mag_without_background = mag - mag_background 
        phase_without_background = phase - phase_background
        #phase_without_background = phase - phase_background + 1
        
        data['Comp Resp'] = 10**(mag_without_background/20)*(np.cos(phase_without_background)+1j*np.sin(phase_without_background))
        data['Resp (dB)'] = mag_without_background
               
        data.to_csv('.\\background_sub_{}_trial_{}.txt'.format(int(i),trial_num),sep = ',',index=False)
        current_file = str(os.getcwd())+'\\background_sub_{}_trial_{}.txt'.format(int(i),trial_num)
        background_subtracted_file_names = np.append(background_subtracted_file_names,[current_file])
    
    return background_subtracted_file_names
        
def linear_normalization(file_names,trial_num):
    normalized_file_names = np.array([])
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        #print(data)
        comp_data = data['Comp Resp'].to_numpy(complex)
        
        mag = data['Resp (dB)'].to_numpy(float)
        mag_first_10 = mag[:10]
        mag_last_10 = mag[-10:]
        mag_reg = np.append(mag_first_10,mag_last_10,axis=0)
        
        '''
        mag = np.abs(comp_data)    
        print(mag)
        mag_first_10 = mag[:10]
        mag_last_10 = mag[-10:]
        mag_reg = np.append(mag_first_10,mag_last_10,axis=0)
        '''
        phase = np.angle(comp_data)
        phase_first_10 = phase[:10]
        phase_last_10 = phase[-10:]
        phase_reg = np.append(phase_first_10,phase_last_10,axis=0)
        
        freq = data['Freq (Hz)'].to_numpy(float)
        freq_first_10 = freq[:10]
        freq_last_10 = freq[-10:]
        freq_reg = np.append(freq_first_10,freq_last_10,axis=0)
        freq_reg = freq_reg.reshape((-1,1))
        
        mag_model = LinearRegression().fit(freq_reg,mag_reg)
        phase_model = LinearRegression().fit(freq_reg,phase_reg)
        
        mag_m = mag_model.coef_
        mag_b = mag_model.intercept_
        
        phase_m = phase_model.coef_
        phase_b = phase_model.intercept_
        
        mag_norm_subtract = linear_equation(freq,mag_m,mag_b)
        
        phase_norm_subtract = linear_equation(freq,phase_m,phase_b)
        
          
        mag_norm = mag - mag_norm_subtract
        phase_norm = phase - phase_norm_subtract
        
        if i == 0:
            extrafig, (extraax1,extraax2) = plt.subplots(nrows=1,ncols=2)
            extraax1.plot(freq/10**9,mag_norm_subtract)
            extraax1.plot(freq/10**9,mag)
            extraax1.plot(freq/10**9,mag_norm)
            extraax2.plot(freq/10**9,phase)
            extraax2.plot(freq/10**9,phase_norm_subtract)
            extraax2.plot(freq/10**9,phase_norm)
            
        
        comp_norm = 10**(mag_norm/20)*(np.cos(phase_norm) + 1j*np.sin(phase_norm))
        #print(comp_norm)
        
        data['Comp Resp'] = comp_norm
        data['Resp (dB)'] = mag_norm
        
        data.to_csv('.\\normalized_{}_trial_{}.txt'.format(int(i),trial_num),sep = ',',index=False)
        current_file = str(os.getcwd())+'\\normalized_{}_trial_{}.txt'.format(int(i),trial_num)
        normalized_file_names = np.append(normalized_file_names,[current_file])
        
    return normalized_file_names

def fit_resonances(file_names,trial_num): 
    fit_file_names = np.array([])
    fit_parameters = pd.DataFrame({'File Num':[],'Resonant Freq':[],'Q':[],'Q_e_imag':[],'Q_e_real':[]})
    #fit_parameters.columns = ['File Num','Resonant Freq','Q','Q_e_imag','Q_e_real']
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        S21_data = data['Comp Resp'].to_numpy(complex)
        f = (data['Freq (Hz)'].to_numpy(float))/10**6
        resonator = ResonatorModel()
        guess = resonator.guess(S21_data, f=f, verbose=True)
        result = resonator.fit(S21_data, params=guess, f=f, verbose=True)

        #print(result.fit_report() + '\n')
        result.params.pretty_print()
        
        fit_s21 = resonator.eval(params=result.params, f=f)
        guess_s21 = resonator.eval(params=guess, f=f)
        
        data['fit'] = fit_s21
        data['guess'] = guess_s21
        
        data.to_csv('.\\fit_{}_trial_{}.txt'.format(int(i),trial_num),sep=',',index=False)
        current_file = str(os.getcwd())+'\\fit_{}_trial_{}.txt'.format(int(i),trial_num)
        fit_file_names = np.append(fit_file_names,[current_file])
        
        #print(type(result.best_values))
        #print(result.best_values)
        current_fit_parameters = pd.DataFrame({'File Num':[i],'Resonant Freq':[result.best_values['f_0']],'Q':[result.best_values['Q']],'Q_e_imag':[result.best_values['Q_e_imag']],'Q_e_real':[result.best_values['Q_e_real']]})
        fit_parameters = pd.concat([fit_parameters,current_fit_parameters],axis=0)
        
        
    #print(fit_parameters)
    param_file = str(os.getcwd()+'\\resonance_parameters_trial_{}.txt'.format(trial_num))
    fit_parameters.to_csv(param_file,sep=',',index=False)    
    return fit_file_names, param_file
 
def plot_ri(data, *args, **kwargs):
    plt.plot(data.real, data.imag, *args, **kwargs)
          
def plot_resonances(file_names,title,out_name,trial_num):
    tot = len(file_names)
    cols = 5
    
    rows = tot // cols
    
    if tot % cols != 0:
        rows += 1
        
    resfig, resax = plt.subplots(rows, cols)
    
    resax = resax.ravel()
    
    for i in range(len(file_names)):
        #print(i)
        data = pd.read_table(file_names[i],sep=',')
        resax[i].plot(data['Freq (Hz)']/10**9,data['Resp (dB)'])
        resax[i].ticklabel_format(useOffset=False)
        resax[i].xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        #resax[i].set_xlabel('Frequency (GHz)')
        #resax[i].set_ylabel('|$S_{21}$| (dB)')
        
    resfig.subplots_adjust(wspace=0.5)
    resfig.subplots_adjust(hspace=0.5)
    resfig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    resfig.suptitle(title) 
    
    resfig = plt.gcf()
    resfig.set_size_inches((12,10), forward=False)
    resfig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\{}_trial_{}.png'.format(out_name,trial_num), dpi=150)       
    plt.close(resfig) 
    
def plot_complex(file_names,title,out_name,trial_num):
    tot = len(file_names)
    cols = 5
    
    rows = tot // cols
    
    if tot % cols != 0:
        rows += 1    
    
    resfig, resax = plt.subplots(rows, cols)
    
    resax = resax.ravel()
    
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        comp = data['Comp Resp'].to_numpy(complex)
        real = comp.real
        imag = comp.imag
        resax[i].plot(real,imag)
        resax[i].ticklabel_format(useOffset=False)
        resax[i].xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        #resax[i].set_xlabel('Re[$S_{21}$]')
        #resax[i].set_ylabel('Im[$S_{21}$]')
        
    resfig.subplots_adjust(wspace=0.5)
    resfig.subplots_adjust(hspace=0.5)
    resfig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    resfig.suptitle(title)   

    resfig = plt.gcf()
    resfig.set_size_inches((12,10), forward=False)
    resfig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)    
    plt.close(resfig)

def plot_fits(file_names,title,out_name,trial_num):
    tot = len(file_names)
    cols = 5
    
    rows = tot // cols
    
    if tot % cols != 0:
        rows += 1    
    
    resfig, resax = plt.subplots(rows, cols)
    
    resax = resax.ravel()
    
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        guess_comp = data['guess'].to_numpy(complex)
        fit_comp = data['fit'].to_numpy(complex)
        resax[i].plot(data['Freq (Hz)']/10**9,data['Resp (dB)'],'o')
        resax[i].plot(data['Freq (Hz)']/10**9,20*np.log10(np.abs(guess_comp)),'--')
        resax[i].plot(data['Freq (Hz)']/10**9,20*np.log10(np.abs(fit_comp)),'-')
        resax[i].ticklabel_format(useOffset=False)
        resax[i].xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        #resax[i].set_xlabel('Frequency (GHz)')
        #resax[i].set_ylabel('|$S_{21}$| (dB)')
        
    resfig.subplots_adjust(wspace=0.5)
    resfig.subplots_adjust(hspace=0.5)
    resfig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    resfig.suptitle(title)  
    
    resfig = plt.gcf()
    resfig.set_size_inches((12,10), forward=False)
    resfig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)
    plt.close(resfig)
    
def plot_fits_complex(file_names,title,out_name,trial_num):
    tot = len(file_names)
    cols = 5
    
    rows = tot // cols
    
    if tot % cols != 0:
        rows += 1    
    
    resfig, resax = plt.subplots(rows, cols)
    
    resax = resax.ravel()
    
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
        
        measured_comp = data['Comp Resp'].to_numpy(complex)
        measured_real = measured_comp.real
        measured_imag = measured_comp.imag
        
        guess_comp = data['guess'].to_numpy(complex)
        guess_real = guess_comp.real
        guess_imag = guess_comp.imag
        
        fit_comp = data['fit'].to_numpy(complex)
        fit_real = fit_comp.real
        fit_imag = fit_comp.imag
        
        
        resax[i].plot(measured_real,measured_imag,'o')
        resax[i].plot(guess_real,guess_imag,'--')
        resax[i].plot(fit_real,fit_imag,'-')
        resax[i].ticklabel_format(useOffset=False)
        resax[i].xaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        #resax[i].set_xlabel('Re[$S_{21}$]')
        #resax[i].set_ylabel('Im[$S_{21}$]')
        
    resfig.subplots_adjust(wspace=0.5)
    resfig.subplots_adjust(hspace=0.5)
    resfig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    resfig.suptitle(title)    
    
    resfig = plt.gcf()
    resfig.set_size_inches((12,10), forward=False)
    resfig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\{}_trial_{}.png'.format(out_name,trial_num),dpi=150)
    plt.close(resfig)

def linear_equation(x,m,b):
    return m*x+b

def linear_resonator(f, f_0, Q, Q_e_real, Q_e_imag):
    Q_e = Q_e_real + 1j*Q_e_imag
    return 1 - (Q * Q_e**-1 / (1 + 2j * Q * (f - f_0) / f_0))

def param_histogram(param_file,bins,trial_num):
    params = pd.read_table(param_file,sep=',')
    params['Resonant Freq']=params['Resonant Freq']/10**3 #convert from MHz to GHz for consistency
    
    histfig, ((histax1,histax2),(histax3,histax4)) = plt.subplots(nrows=2,ncols=2)
    histax1.hist(params['Resonant Freq'],bins)
    histax2.hist(params['Q'],bins)
    histax3.hist(params['Q_e_imag'],bins)
    histax4.hist(params['Q_e_real'],bins)
    
    histax1.set_xlabel('$f_0$ (GHz)',fontsize=14)
    histax2.set_xlabel('$Q$',fontsize=14)
    histax3.set_xlabel('Im[$Q_e$]',fontsize=14)
    histax4.set_xlabel('Re[$Q_e$]',fontsize=14)
    
    histax1.set_ylabel('Number of Resonantors',fontsize=14)
    histax2.set_ylabel('Number of Resonantors',fontsize=14)
    histax3.set_ylabel('Number of Resonantors',fontsize=14)
    histax4.set_ylabel('Number of Resonantors',fontsize=14)
    
    histfig.suptitle('μMUX Chip Characteristics')
    
    resfig = plt.gcf()
    resfig.set_size_inches((12,10), forward=False)
    histfig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\histogram_trial_{}.png'.format(trial_num),dpi=150)
    plt.close(histfig)  
    
if __name__ == "__main__":

    plt.ioff()
    filenames = glob.glob('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\TES_bias_combined_data\\*.txt')
    depth = 37
    width = [2,31]
    window = 300*10**3 #300
        
    #for i in range(1):
    for i in range(len(filenames)):
        print('Processing trial number {}'.format(i))
            
        data = pd.read_table(filenames[i],sep=',')
        
        fig, ax = plt.subplots(1)
        ax.plot(data['Freq (Hz)']/10**9,data['Resp (dB)'])
        fig.suptitle('Resonance Comb',fontsize=16)
        
        if (i==0):
            locs, count = identify_resonances(data, depth, width)
        
            locs_freq = locs['Freq (Hz)'].to_numpy(float)
            locs_resp = locs['Resp (dB)'].to_numpy(float)
            ax.plot(locs['Freq (Hz)']/10**9,locs['Resp (dB)'],'o')
            ax.set_xlabel('Freq (GHz)',fontsize=16)
            ax.set_ylabel('|S21| (dB)',fontsize=16)
        
            fig = plt.gcf()
            fig.set_size_inches((12,10), forward=False)
            fig.savefig('G:\\My Drive\\Stanford\\Kuo_Lab\\VNA_Control_Scripts\\20220810_NIST_Resonator_Box_Data\\Analysis_Scripts\\figures\\res_comb_trial_{}.png'.format(i),dpi=150)
            plt.close(fig)
    
        windowed_file_names = window_resonances(data, locs, window, i)
        plot_resonances(windowed_file_names,'Windowed Resonances (x: Freq (GHz), y: |S21| (dB))','windowed',i)
        plot_complex(windowed_file_names,'Windowed Resoanances (x: Re[S21], y: Im[S21])','windowed_complex',i)
        
        background_subtracted_file_names = remove_background(windowed_file_names, i)
        plot_resonances(background_subtracted_file_names,'Background Removed (x: Freq (GHz), y: |S21| (dB))','background_subtracted',i)
        plot_complex(background_subtracted_file_names,'Background Removed (x: Re[S21], y: Im[S21])','background_subtracted_complex',i)
        
        normalized_file_names = linear_normalization(background_subtracted_file_names, i)
        plot_resonances(normalized_file_names,'Linearly Normalized Resonances (x: Freq (GHz), y: |S21| (dB))','normalized',i)
        plot_complex(normalized_file_names,'Linearly Normalized Resonances (x: Re[S21], y: Im[S21])','normalized_complex',i)
        
        fit_file_names, param_file = fit_resonances(normalized_file_names, i)
        plot_fits(fit_file_names, 'Fits (x: Freq (GHz), y: |S21| (dB))','fits',i)
        plot_fits_complex(fit_file_names, 'Fits (x: Re[S21], y: Im[S21])','fits_complex',i)
        
        param_histogram(param_file, 30, i)
    
    #fit_resonances(normalized_file_names)
    




'''
def identify_resonances(data,depth):
    freq = data['Freq (Hz)'].to_numpy(float)
    resp = data['Resp (dB)'].to_numpy(float)
    
    peaks = PeakDetect(resp,valley=True,thresh=depth)
    ind = peaks.find()
    locs = pd.DataFrame({'Freq (Hz)':[freq[ind]],'Resp (dB)':[resp[ind]]})
    count = len(ind)
    
    return locs, count
'''    

'''
def identify_resonances(data,depth):
    freq = data['Freq (Hz)'].to_numpy(float)
    resp = data['Resp (dB)'].to_numpy(float)
    resonance_ind = argrelextrema(resp, np.less)
    resonance_ind = resonance_ind[0]
    print(resonance_ind)
    print(resp[resonance_ind])
    locs = pd.DataFrame({'Freq (Hz)':[resonance_ind],'Resp (dB)':[resp[resonance_ind]]})
    count = len(resonance_ind)
    print('Found {} resonances deeper than {} dB'.format(count,depth))
    return locs, count
'''

'''
def identify_resonances(data,depth):
    hold = False
    count = 0
    locs = pd.DataFrame({'Freq (Hz)':[],'Resp (dB)':[]})
    for i in range(len(data)):
        if hold == True:
            if data['Resp (dB)'].iloc[i] > depth+1:   #+1 helps handle temporary increases due to noise
                hold = False
                continue
        if (data['Resp (dB)'].iloc[i] <= depth) & (hold == False):            
            newloc = pd.DataFrame({'Freq (Hz)':[data['Freq (Hz)'].iloc[i]],'Resp (dB)':[data['Resp (dB)'].iloc[i]]})
            #print(newloc)
            #print('Approximate Location: ({},{})'.format(data['Freq (Hz)'].iloc[i],data['Resp (dB)'].iloc[i]))
            locs = pd.concat([locs,newloc],axis=0)
            count +=1
            hold = True
    print('Found {} resonances deeper than {} dB'.format(count,depth))
    return locs, count
'''    

'''    
def linear_normalization(file_names):
    normalized_file_names = np.array([])
    for i in range(len(file_names)):
        data = pd.read_table(file_names[i],sep=',')
                
        min_resp = data['Resp (dB)'].min()
        max_resp = data['Resp (dB)'].max()
        data['Resp (dB)'] = data['Resp (dB)'].apply(lambda x: (x-min_resp)/(max_resp-min_resp))
        
        measured_s21 = data['Comp Resp'].to_numpy(dtype=complex)
        real_min = min(measured_s21.real)
        real_max = max(measured_s21.real)
        imag_min = min(measured_s21.imag)
        imag_max = max(measured_s21.imag)
        #normalized_s21 = (measured_s21.real-real_min)/(real_max-real_min)+1j*measured_s21.imag
        normalized_s21 = (measured_s21.real-real_min)/(real_max-real_min)+1j*((measured_s21.imag-imag_min)/(imag_max-imag_min)*(1-(-1))+(-1))
        data['Norm Comp Resp'] = normalized_s21
        
        data.to_csv('.\\normalized_{}.txt'.format(i),sep = ',',index=False)
        current_file = str(os.getcwd())+'\\normalized_{}.txt'.format(int(i))
        normalized_file_names = np.append(normalized_file_names,[current_file])
    return normalized_file_names  
'''        

'''
plt.figure()
plot_ri(S21_data, '.')
plot_ri(fit_s21, '.-', label='best fit')
plot_ri(guess_s21, '--', label='initial fit')
plt.legend()
plt.xlabel('Re(S21)')
plt.ylabel('Im(S21)')

plt.figure()
plt.plot(f, 20*np.log10(np.abs(S21_data)), '.')
plt.plot(f, 20*np.log10(np.abs(fit_s21)), '.-', label='best fit')
plt.plot(f, 20*np.log10(np.abs(guess_s21)), '--', label='initial fit')
plt.legend()
plt.ylabel('|S21| (dB)')
plt.xlabel('MHz')
'''