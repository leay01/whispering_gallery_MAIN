import numpy as np
import pandas as pd 
import cmath 
import scipy.special as sp
import scipy.constants as const
import matplotlib.pyplot as plt


# ------- BESSSEL FUNCTIONS -------
# for TM 
def bessel_roots(m, n): 
    roots = sp.jn_zeros(m, n)
    return roots 

# for TE
def bessel_deriv_roots(m, n):
    roots = sp.jnp_zeros(m, n)
    return roots

# --------- constants ---------

c = const.c

# --------- function based on Jackson's electrodynamics --------

def bessel_omega_freq_solver(mode_kind, num_lobes, p_TE=1): 
    # define constants
    m = num_lobes/2 # number of high-intensity lobes present for that specific mode in COMSOL emw.NormE
    mu = 1 # permeability
    epsilon = 9.6 # dielectric loss -- this is number I was given for alumina 
    d = 0.0254 # height of disk 
    R = 0.0762 # radius of disk 
    n=1 # technically radial index, like how many concentric sets of lobes there are, we focus on modes with just one

    if mode_kind == 'TM': # solve bessel and define p for transverse magnetic (TM)
        x_mn = bessel_roots(m,n)[0]
        p = 0
    if mode_kind == 'TE': # solve bessel and define p for transverse electric (TE) 
        x_mn = bessel_deriv_roots(m,n)[0]
        p = p_TE

    # calculate omega_mnp
    omega_mnp = (c/np.sqrt(mu*epsilon)) * (np.sqrt(((x_mn**2)/(R**2)) + (p**2*np.pi**2)/d**2))
    freq = omega_mnp/(2*np.pi) # Hz
    freq_GHz = freq/(10**9) # GHz

    return freq_GHz


# to get whole TE, TM table based on number of m values desired + input p value for TE modes

def get_TE_TM_m_p(N_m, p_TE=1): 
    m_array = []
    TM_freqs = []
    TE_freqs = []
    for i in range(0, N_m): 
        TM_freq = bessel_omega_freq_solver('TM', num_lobes = i*2)
        TE_freq = bessel_omega_freq_solver('TE', num_lobes = i*2, p_TE=p_TE)
        m_array.append(i)
        TM_freqs.append(TM_freq)
        TE_freqs.append(TE_freq)
    eigenfreqs = {'m': m_array, 'TE': TE_freqs, 'TM': TM_freqs}
    eigen_m_table = pd.DataFrame(eigenfreqs)
    return eigen_m_table

    