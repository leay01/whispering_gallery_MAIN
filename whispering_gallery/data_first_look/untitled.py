import numpy as np 
import pandas as pd
import cmath 
import matplotlib.pyplot as plt
import glob
plt.style.use('dark_background')

def loader(baseline_filename, disk_res_filename): 
    folder_path = '/Users/FTS/Desktop/whispering_gallery/data_test/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    return baseline_data, disk_resonance_data

def loader_plotter(baseline_filename, disk_res_filename): 
    folder_path = '/Users/FTS/Desktop/whispering_gallery/data_test/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    
    fig, ax = plt.subplots(1, 2, figsize = (20,10))
    ax[0].set_title('S21 Comparison')
    ax[0].plot(1e-9*strip_baseline['Freq (Hz)'], 20*np.log10(np.abs(strip_baseline['Complex (decimal)'])), label = 'baseline')
    ax[0].plot(1e-9*disk_strip['Freq (Hz)'], 20*np.log10(np.abs(disk_strip['Complex (decimal)'])), label = 'disk-strip')
    ax[0].legend()
               
    ax[1].set_title('S21, Baseline Subtracted')
    ax[1].plot(1e-9*strip_baseline['Freq (Hz)'], 
                20*np.log10(np.abs(disk_strip['Complex (decimal)']))-20*np.log10(np.abs(strip_baseline['Complex (decimal)'])), label = 'disk - baseline')
    ax[1].legend()
    plt.setp(ax, xlabel = 'Freq (GHz)', ylabel = 'S21 (dB)')
    
    return baseline_data, disk_resonance_data