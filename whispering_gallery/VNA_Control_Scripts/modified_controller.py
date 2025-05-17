'''
modified_controller.py

Description: This scripts allows for control of a Keysight E3631A triple output power supply from a terminal window. The serial port has been hard coded to control the
             power supply connected to heaters on the AliCPT-1 cold stages and focal plane. These heaters allow us to produce load curves and perform enthalpy measurements
             during laboratory testing.

Authors: Chase and Danny - CD

Modifed From: manual_fridge_control.py by Matthew Withers

Editors: Matthew Withers - MW

Change Log
20220628 - CD - Original Script
20220628 - MW - Fixed some small bugs and syntax errors
20220715 - MW - Added lockfile procedure to prevent RS232 collisions

'''


heatersmapfile = 'heaters_map.txt'

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
path='/home/ali/alicpt-hk/lab/general_hk_scripts'
sys.path.insert(0,path)
import instrumentClasses as IC
import datetime as dt
from modified_manualVC import modified_manualVC
from filelock import Timeout, FileLock


outputfile = '/home/ali/alicpt-hk/lab/ali/dev/DevForCD2/Matt/cryostat_heater_control/live_heater_output.txt'
changelog = '/home/ali/alicpt-hk/lab/ali/dev/DevForCD2/Matt/cryostat_heater_control/heater_changes.txt'
selectoutputfile = '/home/ali/alicpt-hk/lab/ali/dev/DevForCD2/Matt/cryostat_heater_control/select_heater_output.txt'

test_output = '/home/ali/alicpt-hk/lab/ali/Ali_cd2/data/test_output.txt'

power_supply = modified_manualVC('ASRL/dev/ttyS8')
lock = FileLock('/run/lock/power_loading_lock.txt.lock')

while True:
	print('\nManual Cryostat Heater Control - For Cold Stage and Focal Plane Heaters \n')

	function = input('Select an operation:\n[1] Print Status of Supplies\n[2] Print Voltages\n[3] Print Currents\n[4] Change Supply States\n[5] Change Voltages\n[6] Record Voltages and Currents\n[7] Exit\nSelection: ')
	print('\n')
	if function == '1':
		print('Status (1 = output ON; 0 = output OFF):\n')
		lock.acquire()
		power_supply.get_state()
		lock.release()
	elif function == '2':
		print('Voltages (V):')
		lock.acquire()
		power_supply.get_voltage()
		lock.release()
	elif function == '3':
		print('Current (A):')
		lock.acquire()
		power_supply.get_current()
		lock.release()
	elif function == '4':
		print('Change Supply State\nEnter [1] for output ON; [0] for output OFF; [None] for output unchanged')
		state = input('Left Supply, Right Supply: ')
		if (state == 'None'):
			lock.acquire()
			power_supply.set_state(None)
			lock.release()
		elif (state != 'None'):
			lock.acquire()
			power_supply.set_state(float(state))
			lock.release()
	elif function == '5':
		channel1, channel2, channel3 = power_supply.get_voltage()
		print('Change Voltages\nInput new voltages in V by channel\n')
		arg = input('Choose channel to modify\n[*] for all; [1/2/3] for specific one: ')
		if (arg == '*'):
			channel1, channel2, channel3 = input('channel 1, channel 2, channel3: ').split()
			print(channel1, channel2, channel3)
			lock.acquire()
			power_supply.set_volt(float(channel1), float(channel2), float(channel3), changelog)
			lock.release()
		elif (str(arg) == '1'):
			channel1 = input(f'new {arg} value: ')
			lock.acquire()
			power_supply.set_volt(float(channel1), float(channel2), float(channel3), changelog)
			lock.release()
		elif (str(arg) == '2'):
			channel2 = input(f'new {arg} value: ')
			lock.acquire()
			power_supply.set_volt(float(channel1), float(channel2), float(channel3), changelog)
			lock.release()
		elif (str(arg) == '3'):
			channel3 = input(f'new {arg} value: ')
			lock.acquire()
			power_supply.set_volt(float(channel1), float(channel2), float(channel3), changelog)
			lock.release()
		else:
			print('Not a valid argument!')
	elif function == '6':
		print('Recording to: '+selectoutputfile)
		lock.acquire()
		power_supply.write_data(selectoutputfile)
		lock.release()
	elif function == '7':
		print('Exiting...')
		exit()
	else:
		print('Invalid option.\n')


# In[ ]:




