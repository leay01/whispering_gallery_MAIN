#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
manualVC.py


'''
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#path='/home/ali/alicpt-hk/lab/general_hk_scripts'
#sys.path.insert(0,path)
import instrumentClasses as IC
import datetime as dt

class modified_manualVC:
	def __init__(self, supply):
		self.supply = supply
		self.digits = 3
	def get_state(self):
		state = IC.E3631.Output(self.supply,'?')
		print('state = '+state)
	def get_voltage(self):
		outputs1 = IC.E3631.readAll(self.supply, 1)
		outputs2 = IC.E3631.readAll(self.supply, 2)
		outputs3 = IC.E3631.readAll(self.supply, 3)
		
		c1 = round(float(outputs1[0]),self.digits)
		c2 = round(float(outputs2[0]),self.digits)
		c3 = round(float(outputs3[0]),self.digits)
				
		print('Channel 1 = '+str(c1)+'\nChannel 2 = '+str(c2)+'\nChannel 3 = '+str(c3))
		return(c1, c2, c3)
	def get_current(self):
		outputs1 = IC.E3631.readAll(self.supply, 1)
		outputs2 = IC.E3631.readAll(self.supply, 2)
		outputs3 = IC.E3631.readAll(self.supply, 3)
		
		c1 = round(float(outputs1[0]),self.digits)
		c2 = round(float(outputs2[0]),self.digits)
		c3 = round(float(outputs3[0]),self.digits)
				
		print('Channel 1 = '+str(c1)+'\nChannel 2 = '+str(c2)+'\nChannel 3 = '+str(c3))
		return(c1, c2, c3)
	def set_state(self, state = None):
		if (state == 1):
			IC.E3631.Output(self.supply, 1)
			print('\nNew state:')
			self.get_state()
		if (state == 0):
			IC.E3631.Output(self.supply, 0)
			print('\nNew state:')
			self.get_state()
		if (state == None):
			print('\nNew state:')
			self.get_state()
              
	def set_volt(self, setV_c1 = None, setV_c2 = None, setV_c3 = None, datafile = '/home'):
		if setV_c1 != None:
			if (setV_c1 >= 0) & (setV_c1 <= 6): 
				IC.E3631.writeV(self.supply, 1, setV_c1)
			else:
				print('Voltage for channel 1 out of bounds. Must be between 0 V and 6 V.')
		if setV_c2 != None:
			if (setV_c2 >= 0) & (setV_c2 <= 25): 
				IC.E3631.writeV(self.supply, 2, setV_c2)
			else:
				print('Voltage for channel 2 out of bounds. Must be between 0 V and 25 V.')
		if setV_c3 != None:
			if (setV_c3 <= 0) & (setV_c3 >= -25): 
				IC.E3631.writeV(self.supply, 3, setV_c3)
			else:
				print('Voltage for channel 3 out of bounds. Must be between -25 V and 0 V.')
		self.get_voltage()
		self.write_data(datafile)
	def write_data(self, outputfile):
		with open(outputfile, 'a') as f:
			if os.path.getsize(outputfile) == 0:
				f.write('datetime'+','+'channel 1 (V)'+','+'channel 1 (A)'+','+'channel 2 (V)'+','+'channel 2 (A)'+','+'channel 3 (V)'+','+'channel 3 (A)'+'\n')
			f.write(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			for i in np.arange(1,4,1):
				(Vl,Il,Ol) = IC.E3631.readAll(self.supply, i)
				f.write(','+Vl.rstrip()+','+Il.rstrip())
			f.write('\n')
			f.close()
						  	 	 



#power_supply.get_state()

#power_supply.set_state(1,1)

#power_supply.set_volt(6,6,None,6,6,-6)

#power_supply.get_current()



#print(power_supply.left)

#print(IC.E3631.Output(left_supply,'?'))
#IC.E3631.writeV(left_supply,1,4)
#IC.E3631.writeV(left_supply,2,5)

#IC.E3631.Output('ASRL/dev/ttyS5', 0)

