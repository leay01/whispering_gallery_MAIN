
# useful functions for recent analysis

import numpy as np
import pandas as pd 
import cmath 
import scipy.special as sp
import scipy.signal as spg
import scipy.constants as const
import matplotlib.pyplot as plt


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