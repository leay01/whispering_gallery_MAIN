import numpy as np 
import pandas as pd
import cmath 
import matplotlib.pyplot as plt
import glob
plt.style.use('dark_background')
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.titlesize'] = 24
plt.rcParams['legend.fontsize'] = 15



def loader(baseline_filename, disk_res_filename, folder): 
    folder_path = '/Users/leayamashiro/whispering_gallery_MAIN/whispering_gallery/' + folder + '/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    return baseline_data, disk_resonance_data

def loader_plotter(baseline_filename, disk_res_filename, folder):
    folder_path = '/Users/leayamashiro/whispering_gallery_MAIN/whispering_gallery/' + folder + '/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    
    fig, ax = plt.subplots(3, 1, figsize = (20,25))
    
    ax[0].set_title('21 Baseline')
    ax[0].plot(1e-9*baseline_data['Freq (Hz)'], 20*np.log10(np.abs(baseline_data['Complex (decimal)'])), label = '(strip) baseline', color = 'red')
    ax[0].legend()
    ax[0].set_ylim(np.min(20*np.log10(np.abs(disk_resonance_data['Complex (decimal)']))), np.max(20*np.log10(np.abs(baseline_data['Complex (decimal)'])))+0.5)
    
    ax[1].set_title('S21 Comparison')
    ax[1].plot(1e-9*baseline_data['Freq (Hz)'], 20*np.log10(np.abs(baseline_data['Complex (decimal)'])), label = '(strip) baseline', color = 'red')
    ax[1].plot(1e-9*disk_resonance_data['Freq (Hz)'], 20*np.log10(np.abs(disk_resonance_data['Complex (decimal)'])), label = 'disk + strip')
    ax[1].legend()
               
    ax[2].set_title('S21, Baseline Subtracted')
    ax[2].plot(1e-9*baseline_data['Freq (Hz)'], 
                20*np.log10(np.abs(disk_resonance_data['Complex (decimal)']))-20*np.log10(np.abs(baseline_data['Complex (decimal)'])), 
               label = '(disk + strip) - baseline', color = 'orange')
    ax[2].legend()
    plt.setp(ax, xlabel = 'Freq (GHz)', ylabel = 'S21 (dB)')
    #plt.suptitle('Alumina Disk-Microstrip WGM Transmission Testing', fontsize = 28)
    
   # plt.tight_layout()
    
    return baseline_data, disk_resonance_data

def loader_plotter_chunk(baseline_filename, disk_res_filename, folder, plot_start, plot_stop):
    folder_path = '/Users/leayamashiro/whispering_gallery_MAIN/whispering_gallery/' + folder + '/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    
    fig, ax = plt.subplots(3, 1, figsize = (20,25))
    
    ax[0].set_title('21 Baseline')
    ax[0].plot(1e-9*baseline_data['Freq (Hz)'], 20*np.log10(np.abs(baseline_data['Complex (decimal)'])), label = '(strip) baseline', color = 'red')
    ax[0].legend()
    ax[0].set_ylim(np.min(20*np.log10(np.abs(disk_resonance_data['Complex (decimal)']))), np.max(20*np.log10(np.abs(baseline_data['Complex (decimal)'])))+0.5)
    ax[0].set_xlim(plot_start, plot_stop)

    ax[1].set_title('S21 Comparison')
    ax[1].plot(1e-9*baseline_data['Freq (Hz)'], 20*np.log10(np.abs(baseline_data['Complex (decimal)'])), label = '(strip) baseline', color = 'red')
    ax[1].plot(1e-9*disk_resonance_data['Freq (Hz)'], 20*np.log10(np.abs(disk_resonance_data['Complex (decimal)'])), label = 'disk + strip')
    ax[1].legend()
    ax[1].set_xlim(plot_start, plot_stop)
               
    ax[2].set_title('S21, Baseline Subtracted')
    ax[2].plot(1e-9*baseline_data['Freq (Hz)'], 
                20*np.log10(np.abs(disk_resonance_data['Complex (decimal)']))-20*np.log10(np.abs(baseline_data['Complex (decimal)'])), 
               label = '(disk + strip) - baseline', color = 'orange')
    ax[2].legend()
    ax[2].set_xlim(plot_start, plot_stop)

    plt.setp(ax, xlabel = 'Freq (GHz)', ylabel = 'S21 (dB)')
    #plt.suptitle('Alumina Disk-Microstrip WGM Transmission Testing', fontsize = 28)
    
   # plt.tight_layout()
    
    return baseline_data, disk_resonance_data

