
# useful functions for recent analysis

import numpy as np
import pandas as pd 
import cmath 
import scipy.special as sp
import scipy.signal as spg
import scipy.constants as const
import matplotlib.pyplot as plt



# ---------------- FOR COMSOL DATA in CSV FORM ----------------------
# for pulling peak Q factors out of *STEPPED* COMSOL eigenfrequency data, returns a dictionary of the indices
# of the top 10 Q factor peaks for each set, ex: 
# {0: {'CF': 1000000000, 'indices': Index([209, 167, 197, 131, 34, 160, 103, 36, 30], dtype='int64')},
def peak_index_finder(Q_set, param_array): 
    peak_index_dict = {}
    peak_table_step_list = []
    for i in range(len(param_array)):
        signal_step_i = Q_set[Q_set['% search_freq (Hz)']==params[i]].reset_index(inplace=False)
        peaks_i, _ = spg.find_peaks(signal_step_i['Quality factor (1)'])
        Q_peaks_i = signal_step_i.loc[peaks_i].sort_values('Quality factor (1)', ascending=False)
        Qpeaks_top10 = Q_peaks_i.iloc[0:9]
        peak_table_step_list.append(Qpeaks_top10)
        peak_index_dict[i] = {'CF': param_array[i], 'indices': Qpeaks_top10.index}
    return peak_index_dict, peak_table_step_list


# for fixing the complex numbers in csv that comes out of COMSOL eigenfrequency data
def fix_csv(filename, filepath): 
    file = pd.read_csv(filepath + filename, skiprows=4)
    # Define a function to convert string representation to complex number
    def convert_to_j(x):
        if isinstance(x, str):  # Only try to convert if it's a string
            try:
                return x.replace('i', 'j')  # Replace 'i' with 'j' for Python compatibility
            except ValueError:
                return None  # Return None for invalid values (if any)
        else:
            return x  # If it's already a number (e.g., float), return it unchanged
    file['% Eigenfrequency (GHz)'] = file['% Eigenfrequency (GHz)'].apply(convert_to_j) # convert i to j for column 
    file['% Eigenfrequency (GHz)'] = file['% Eigenfrequency (GHz)'].apply(complex)
    file[['Frequency (GHz)', 'Quality factor (1)']] = file[['Frequency (GHz)', 'Quality factor (1)']].apply(pd.to_numeric, errors='coerce')
    return file     


# from COMSOL, finding and plotting the peaks, having already loaded in data: 

def find_plot_Q_peaks(Q_freq_data):
    # clean up work for TE doubles in Q1to5
    Q_freq_data['Freq rounded'] = Q_freq_data['Frequency (GHz)'].round(5)
    # Step 3: Drop duplicates, keeping the first occurrence
    Qfac_all = Q_freq_data.drop_duplicates(subset='Freq rounded', keep='first')
    Q_peaks, _ = spg.find_peaks(Qfac_all['Quality factor (1)'])
    Q_peak_freqs = Qfac_all['Frequency (GHz)'].iloc[Q_peaks]
    Q_peak_Qs = Qfac_all['Quality factor (1)'].iloc[Q_peaks]
    Q_cfs = Qfac_all['% search_freq (Hz)'].iloc[Q_peaks]
    peak_dict = {'cf': Q_cfs, 'freqs': Q_peak_freqs, 'Q': Q_peak_Qs}
    peaks = pd.DataFrame(peak_dict).sort_values('Q', ascending=False).reset_index(inplace=False)
    top_peaks = peaks.iloc[0:20]

    # plot with peaks labeled
    plt.plot(Qfac_all['Frequency (GHz)'], Qfac_all['Quality factor (1)'])
    plt.xlabel('Freq (GHz)')
    plt.ylabel('Q factor')
    plt.title('Q Factor vs. Eigenfrequency')

    for i in range(len(top_peaks)):
        plt.scatter(top_peaks['freqs'].loc[i], top_peaks['Q'].loc[i], 
                    label = f'({top_peaks["freqs"][i]} GHz, {top_peaks["Q"][i]})')
    plt.legend()

    return Qfac_all, top_peaks





# -------------------------- for VNA DATA, .txt form ----------------------------

def just_single_loader(path): # just to load in data and fix the parentheses and complex data
    #folder_path = '/Users/FTS/Desktop/whispering_gallery/'
    data = pd.read_csv(path)
    data['Complex (decimal)'] = data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    return data

def loader(baseline_filename, disk_res_filename, folder): # to load in a pair of baseline and signal data 
    folder_path = '/Users/leayamashiro/whispering_gallery_MAIN/whispering_gallery/' + folder + '/'
    baseline_data = pd.read_csv(folder_path + baseline_filename)
    baseline_data['Complex (decimal)'] = baseline_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    disk_resonance_data = pd.read_csv(folder_path + disk_res_filename)
    disk_resonance_data['Complex (decimal)'] = disk_resonance_data['Complex (decimal)'].str.replace(r'[()]', '', regex=True).apply(complex)
    return baseline_data, disk_resonance_data

def loader_plotter(baseline_filename, disk_res_filename, folder): # same as above, but to plot them and plot the subtraction "calibration"
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

def loader_plotter_chunk(baseline_filename, disk_res_filename, folder, plot_start, plot_stop): # same as above, just for a specific chunk of frequency
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


def find_plot_dips(BL, disk, n_dips, f_start=None, f_stop=None, title = 'title'): # for S21 dips in VNA data, need to already have baseline & disk data loaded in as variables

    # prepare signal data 
    S21_subtracted = (20*np.log10(np.abs(disk['Complex (decimal)']))
                  -20*np.log10(np.abs(BL['Complex (decimal)']))) # just to get the calibrated one ready
    S21_freqs = 1e-9*BL['Freq (Hz)'] # convert to GHz
    S21_sub = pd.DataFrame({'freqs':S21_freqs, 'S21':S21_subtracted}) # make calibrated data dictionary
    if (f_start is not None) and (f_stop is not None): 
        S21_subt = S21_sub[(S21_sub['freqs']>=f_start) & (S21_sub['freqs']<=f_stop)]
    else: 
        S21_subt = S21_sub
    # peak finding
    S21_dips, _dips = spg.find_peaks(-S21_subt['S21']) # negative because need to flip
    dip_freqs = S21_subt['freqs'].iloc[S21_dips] # get frequency values for dips
    dip_S21 = S21_subt['S21'].iloc[S21_dips] # get S21 of the located dips
    dip_dict = {'freqs': dip_freqs, 'dip S21': dip_S21} # make dip dictionary
    dips_sorted = pd.DataFrame(dip_dict).sort_values('dip S21', ascending=True).reset_index(inplace=False) # make DF where dips sorted by mag
    top_dips = dips_sorted.iloc[0:n_dips] # grab top 10 deepest dips

    plt.figure(figsize = (17,13))
    plt.plot(S21_subt['freqs'], S21_subt['S21'])
    for i in range(len(top_dips)):
        plt.scatter(top_dips['freqs'].loc[i], top_dips['dip S21'].loc[i], 
                    label = f'({top_dips["freqs"][i]} GHz, {top_dips["dip S21"][i]})')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (arb)')
    plt.title(title)
    plt.legend()
    return S21_subt, dips_sorted

def find_plot_Q_peaks(Q_freq_data):
    # clean up work for TE doubles in Q1to5
    Q_freq_data['Freq rounded'] = Q_freq_data['Frequency (GHz)'].round(5)
    # Step 3: Drop duplicates, keeping the first occurrence
    Qfac_all = Q_freq_data.drop_duplicates(subset='Freq rounded', keep='first')
    Q_peaks, _ = spg.find_peaks(Qfac_all['Quality factor (1)'])
    Q_peak_freqs = Qfac_all['Frequency (GHz)'].iloc[Q_peaks]
    Q_peak_Qs = Qfac_all['Quality factor (1)'].iloc[Q_peaks]
    Q_cfs = Qfac_all['% search_freq (Hz)'].iloc[Q_peaks]
    peak_dict = {'cf': Q_cfs, 'freqs': Q_peak_freqs, 'Q': Q_peak_Qs}
    peaks = pd.DataFrame(peak_dict).sort_values('Q', ascending=False).reset_index(inplace=False)
    top_peaks = peaks.iloc[0:20]

    plt.figure(figsize = (15,10))
    # plot with peaks labeled
    plt.plot(Qfac_all['Frequency (GHz)'], Qfac_all['Quality factor (1)'])
    plt.xlabel('Freq (GHz)')
    plt.ylabel('Q factor')
    plt.title('Q Factor vs. Eigenfrequency')

    for i in range(len(top_peaks)):
        plt.scatter(top_peaks['freqs'].loc[i], top_peaks['Q'].loc[i], 
                    label = f'({top_peaks["freqs"][i]} GHz, {top_peaks["Q"][i]})')
    plt.legend()

    return Qfac_all, top_peaks

