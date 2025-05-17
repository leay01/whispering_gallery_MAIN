"""
Instrument Classes

Creates classes to store, organize and retrieve information from SIM900, SIM922
and other instruments easily. It also has a virtualInstrument() class that creates a virtual
instrument with the bare minimum functions to run code when we don't have access to
a real instrument.

To learn more about how classes work:
https://techwithtim.net/tutorials/python-programming/classes-objects-in-python/creating-classes/

Author: Jordi Montana-Lopez - JM

Editors: Matthew Withers - MW

Change Log:

202008   - JM - original script
20220725 - MW - added try...except statement structure around instrument queries in E3631.readAll(), E3631.readV(), and E3631.readI() to check and handle timeout errors; if
                   a timeout error occurs, the program returns a message and reattempts the query.
20220804 - MW - added methods to the SIM960 class which query / set the lower and upper voltage outputs


"""
import matplotlib.pyplot as plt
import random
import datetime as dt
import pyvisa
#from interpolation import interpolateDiode
import numpy as np

'''
------------------------------------------------------------------------------
Virtual instrument
------------------------------------------------------------------------------
'''

class virtualInstrument():
    '''
    Placeholder function that helps run the code while we can't connect to the instrument.
    It mirrors some of the functions you woud get from:
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource('some_port_number')

    Use case: are away from the lab but want to run and debug code that uses the instrument.
    Do: comment out the next two lines and add the last one
        #rm = pyvisa.ResourceManager()
        #SIM900_1 = SIM900(rm.open_resource('ASRL3::INSTR'))
        SIM900_1 = SIM900(virtualInstrument())

        Then use the new SIM900_1 variable the way you would expect it to work if it were the plugged instrument.
    '''

    ID = 'This is a placeholder resource.'
    dontKnow = ID + ' This command was not understood. It might work with the plugged instrument.'

    def query(self,text):
        if text == '*IDN?':
            print(self.ID)
            return self.ID

        if text == 'VOLT?0,1':
            # This emulates voltage readout where the values are random
            # Values obtained from the interpolation file
            maxD760 = 1.64429
            minD760 = 0.090618
            ch1 = random.uniform(minD760,maxD760)
            ch2 = random.uniform(minD760,maxD760)
            ch3 = random.uniform(minD760,maxD760)
            ch4 = random.uniform(minD760,maxD760)
            return str(ch1) + ',' + str(ch2) + ',' + str(ch3) + ',' + str(ch4)

        if text == 'APPL? P6V': return '6'
        if text == 'APPL? P25V': return '25'
        if text == 'APPL? N25V': return '-25'

        else:
            print(self.dontKnow + 'I received: ' + text)
            return self.dontKnow

    def write(self,text):
        print('This resource wrote: '+ text)

    def close(self):
        print('This resource is closed.')

'''
SIM Generic Class
'''
class SIMGenericClass():
    '''
    This has the most basic functions that all instruments need. New instrument
    classes can be built from this one by adding more functions. Example:

    class SIMNewInstrument(SIMGenericClass):
        def functionSpecificToNewInstrument():
            ...

    Now even though SIMNewInstrument only has one function, it also has all
    the functions from SIMGenericClass.
    '''
    def __init__(self,SIM900,slot):
        self.mainframe = SIM900
        self.slot = slot
        self.write('*CLS')
        self.write('*RST')

    def write(self,command):
        escapeStr = 'slot'+str(self.slot)
        self.mainframe.write('CONN ' + str(self.slot)+',"' + escapeStr+'"')
        self.mainframe.write(command)
        self.mainframe.write(escapeStr)

    def read(self):
        return self.mainframe.read()

    def query(self,command):
        escapeStr = 'slot'+str(self.slot)
        self.mainframe.write('CONN ' + str(self.slot)+',"' + escapeStr+'"')
        response = self.mainframe.query(command)
        self.mainframe.write(escapeStr)
        return response


'''
------------------------------------------------------------------------------
SIM 922
------------------------------------------------------------------------------
'''
'''
class SIM922Class(SIMGenericClass):
    ch1 = [[],[]]
    ch2 = [[],[]]
    ch3 = [[],[]]
    ch4 = [[],[]]

    t = []

    def __init__(self,SIM900,slot):
        SIMGenericClass.__init__(self,SIM900,slot)
        self.write('SRST')
        self.IDN = self.query('*IDN?')

    def getChannel(self,number):
        if number == 1: return self.ch1
        if number == 2: return self.ch2
        if number == 3: return self.ch3
        if number == 4: return self.ch4

    def command(self,command,value):
        if command == 'BAUD': self.BAUD = value
        elif command == 'SBIT': self.SBIT = value
        elif command == 'PARI': self.PARI = value
        elif command == 'FLOW': self.FLOW = value
        elif command == 'TMOT': self.TMOT =value
        else:
            print('SIM922 got ' + str(command) + ' with value ' + str(value))

    def readV(self):
        self.mainframe.write('CONN '+ str(self.slot) + ',"slot'+str(self.slot)+'"') # Connect to the slot
        datetime = dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
        self.t.append(datetime)
        rawData = self.mainframe.query('VOLT?0,1').strip('\r\n').split(',')
        rawData = [float(elt) for elt in rawData]
        self.mainframe.write('slot'+str(self.slot))

        # Do calibration with the standard curve of the DT670
        FourChCalData = []
        for channel in range(1,5):
            calibratedData = interpolateDiode(float(rawData[channel-1]))
            FourChCalData.append(calibratedData)
            self.mainframe.getSlot(self.slot).getChannel(channel)[0].append(rawData)
            self.mainframe.getSlot(self.slot).getChannel(channel)[1].append(calibratedData)

        # Write in a file
        with open('SIM900_' + str(self.mainframe.label) + '_SIM922_' + str(self.slot)+ '.txt', 'a') as f:
            f.write('%s, %f, %f, %f, %f, %f, %f, %f, %f\n' %(datetime, rawData[0], rawData[1], rawData[2],\
                    rawData[3], FourChCalData[0], FourChCalData[1], FourChCalData[2], FourChCalData[3]))

    def load(self,times,ch1,ch2,ch3,ch4):
        self.t = times
        self.ch1 = ch1
        self.ch2 = ch2
        self.ch3 = ch3
        self.ch4 = ch4

'''
def read922(name = 'SIM900_1_SIM922_1.txt',start = 0, end = None):
    '''
    import os
    with open(name, 'rb') as f:
        f.seek(-2,os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2,os.SEEK_CUR)
        last_line = f.readline().decode()
    [TODO] only read last 10 lines of the file, so you dont need to load a huge file
    '''
    with open(name,'r') as f:
        file = f.readlines()
    lines = file[start:end]
    times = []
    ch1 = [[],[]]
    ch2 = [[],[]]
    ch3 = [[],[]]
    ch4 = [[],[]]
    for line in lines:
        line = line.strip('\n').split(', ')
        times.append(line[0]+ ' ' + line[1])
        ch1[0].append(float(line[2]))
        ch2[0].append(float(line[3]))
        ch3[0].append(float(line[4]))
        ch4[0].append(float(line[5]))
        ch1[1].append(float(line[6]))
        ch2[1].append(float(line[7]))
        ch3[1].append(float(line[8]))
        ch4[1].append(float(line[9]))

    return times,ch1,ch2,ch3,ch4

def mainframeLabelSlot(name = 'SIM900_1_SIM922_1.txt'):
    name = name.replace('SIM900_','')
    mainframeLabel = name[:name.index('_')]
    name = name[name.index('_'):]
    name = name.replace('_SIM922_','')
    slot = name[:name.index('.')]
    return mainframeLabel, slot

def plotDiodes(name = ['SIM900_1_SIM922_1.txt'], start = 0, end = None):
    width = 40
    height = 20
    plt.figure(1, figsize = (width, height))
    plt.clf()
    plt.subplot(1,2,1)
    for txtFile in name:
        t,ch1,ch2,ch3,ch4 = read922(txtFile,start,end)
        t = [dt.datetime.strptime(elt,'%m/%d/%Y %H:%M:%S') for elt in t]
        t = [(elt - t[0]).total_seconds() for elt in t]
        mfLabel,slot = mainframeLabelSlot(txtFile)

        plt.plot(t[start:end], ch1[1][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch1')
        plt.plot(t[start:end], ch2[1][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch2')
        plt.plot(t[start:end], ch3[1][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch3')
        plt.plot(t[start:end], ch4[1][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch4')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperature (K)")
    plt.title("Calibrated SIM922 Data")
    plt.legend(loc = 'upper right')

    plt.subplot(1,2,2)
    for txtFile in name:
        t,ch1,ch2,ch3,ch4 = read922(txtFile,start,end)
        t = [dt.datetime.strptime(elt,'%m/%d/%Y %H:%M:%S') for elt in t]
        t = [(elt - t[0]).total_seconds() for elt in t]
        mfLabel,slot = mainframeLabelSlot(txtFile)
        plt.plot(t[start:end], ch1[0][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch1')
        plt.plot(t[start:end], ch2[0][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch2')
        plt.plot(t[start:end], ch3[0][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch3')
        plt.plot(t[start:end], ch4[0][start:end], '.-', label = 'Mf ' + mfLabel + ' Slot '+ slot +' Ch4')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Voltage (V)")
    plt.title("Raw SIM922 Data")
    plt.legend(loc = 'upper right')
    plt.show()

'''
------------------------------------------------------------------------------
SIM 900
------------------------------------------------------------------------------
'''
class SIM900Class:
    '''
    Stores information about the SIM900 intuitively, what sensors it has in each port,
    and allows access to the PyVisa resource. For example:
        rm = pyvisa.ResourceManager()
        SIM900_1 = SIM900(rm.open_resource('ASRL3::INSTR'))


    If you are not connected to the instrument, use:
        SIM900_1 = SIM900(virtualInstrument())
    '''

    def __init__(self,SIM900,slot,label = 1):
        self.mainframe = SIM900
        self.label = label # Number on a physical sticker on the mainframe
        self.slot = slot
        self.presets()
        self.IDN = self.query('*IDN?')

    def presets(self):
        self.write('*CLS')
        self.write('*RST')
        self.write('SRST')
        for slot in range(1,7):
            self.write('BAUD ' + str(slot) + ',9600')
            self.write('PARI ' + str(slot) + ',None')
            self.write('WORD ' + str(slot) + ',8')
            self.write('SBIT ' + str(slot) + ',1')
            self.write('TMOUT ' + str(slot) + ',10000')

    def setSlot(self,number,sensor):
        if number == 1: self.slot1 = sensor
        elif number == 2: self.slot2 = sensor
        elif number == 3: self.slot3 = sensor
        elif number == 4: self.slot4 = sensor
        elif number == 5: self.slot5 = sensor
        elif number == 6: self.slot6 = sensor
        elif number == 7: self.slot7 = sensor
        elif number == 8: self.slot8 = sensor
        else:
            print('Invalid input.')

    def getSlot(self,number):
        if number == 1: return self.slot1
        elif number == 2: return self.slot2
        elif number == 3: return self.slot3
        elif number == 4: return self.slot4
        elif number == 5: return self.slot5
        elif number == 6: return self.slot6
        elif number == 7: return self.slot7
        elif number == 8: return self.slot8
        else:
            print('Invalid "get" input.')

    def write(self,SIM900command):
        self.mainframe.write(SIM900command)

    def plot(self,pause = 1):
        plt.figure(1, figsize = (16, 11))
        plt.clf()
        for slot in range(1,7):
            plt.subplot(2,4,slot)
            plt.plot(self.getSlot(slot).t[-10:], self.getSlot(slot).ch1[-10:], 'go-', label = 'Ch1')
            plt.plot(self.getSlot(slot).t[-10:], self.getSlot(slot).ch2[-10:], 'bo-', label = 'Ch2')
            plt.plot(self.getSlot(slot).t[-10:], self.getSlot(slot).ch3[-10:], 'ro-', label = 'Ch3')
            plt.plot(self.getSlot(slot).t[-10:], self.getSlot(slot).ch4[-10:], 'ko-', label = 'Ch4')
            plt.xlabel("Time (second)")
            plt.ylabel("Temperature (K)")
            plt.title("SIM922 #" + str(3+slot))
            plt.legend(loc = 'upper right')
            plt.gcf().autofmt_xdate()

        plt.subplots_adjust(wspace = 0.4)
        plt.pause(pause)

    def query(self,text):
        return self.mainframe.query(text)

    def read(self):
        return self.mainframe.read()

    def terminate(self):
        self.write('*CLS')
        self.write('*RST')
        self.mainframe.close()

def initializeSIM900(SIM900_input):
    '''
    Initialize instruments
    '''
    instrumentsConnected = input('Is the SIM900 physically connected to the computer?[yes/no]')
    if instrumentsConnected == 'yes' or instrumentsConnected == 'y':
        # Search for the port on the host computer that is used to connect the SIM900#3 via RS-232 cable.
        rm = pyvisa.ResourceManager() #go to the visa library
        ID = rm.list_resources()
        print('These are the ports where the instruments are connected:')
        print(ID)
        try:
            port = SIM900_input['port']
            SIM900 = SIM900Class(rm.open_resource(port),port)
        except:
            arraySlot =  int(input('In which position in this array is the port for SIM900? (0,1,2,...)'))
            SIM900 = SIM900Class(rm.open_resource(ID[arraySlot]),ID[arraySlot])

        SIM900.write('*CLS')
        SIM900.write('*RST')
        #print(SIM900.query('*IDN?')) # first identification

    else:
        SIM900 = SIM900Class(virtualInstrument(),'virtualPort')

        # Start the 1-6 slots of the SIM900 mainframe as SIM922 sensors
        for slot in range(1,7):
            SIM900.setSlot(slot,SIM922Class())

    return SIM900


def parseSIM900(SIM900command):
    '''
    Parses common SIM900 code strings into which command needs to be updated, in which slot, and to what value
    '''
    command, arguments = SIM900command.split(' ',1)
    if command == 'BAUD' or command == 'SBIT' or command == 'PARI' or command == 'FLOW' or command == 'TMOT' or command == 'CONN':
        slot, value = arguments.split(',')
    else:
        return 'Error'
    return command,slot,value


'''
------------------------------------------------------------------------------
Keysight power supply
------------------------------------------------------------------------------
'''
def initializePS(PS_input):
    '''
    Initialize power supply
    '''
    instrumentsConnected = input('Is the power supply physically connected to the computer?[yes/no]')
    if instrumentsConnected == 'yes' or instrumentsConnected == 'y':
        # Initialize the Keysight E3631A DC Power Supply, ask the user for starting values
        rm = pyvisa.ResourceManager() #go to the visa library
        ID = rm.list_resources()
        print(ID)
        try:
            port = PS_input['port']
            KeysightPS =KeysightPSClass(rm.open_resource(port),port)
        except:
            arraySlot =  int(input('In which position in this array is the port for Keysight PS? (0,1,2,...)'))
            KeysightPS =KeysightPSClass(rm.open_resource(ID[arraySlot]),port)

        print(KeysightPS.query('*IDN?')) # first identification

    else:
        KeysightPS = KeysightPSClass(virtualInstrument())


    KeysightPS.write('SYST:REM')
    KeysightPS.write('OUTP ON')

    # Your input values will be input to the Keysight
    for port in ['P6V','P25V','N25V']:
        KeysightPS.setSlot(port,PS_input[port])

    return KeysightPS


def readAndPlotPS(KeysightPS):
    '''
    Take measurements and plot the last few
    '''
    dateTime = dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    KeysightPS.readout(dateTime)
    KeysightPS.plot(pause = 1)

class KeysightPSClass:
    '''
    Stores information about the Keysight E631A Power Supply intuitively, what sensors it has in each port,
    and allows access to the PyVisa resource.
    Example:
        rm = pyvisa.ResourceManager()
        KeysightPS_1 = KeysightPSClass(rm.open_resource('ASRL3::INSTR'))

    If you are not connected to the instrument, use:
        KeysightPS_1 = KeysightPSClass(virtualInstrument())
    '''
    P6V = []
    P25V = []
    N25V = []
    t = []

    def __init__(self,resource,port):
        self.resource = resource
        self.port = port

    def setPort(self,port,value = ()):
        if value == (): # If nothing was sent
            value = float(input('Set the voltage value for the ' + str(port) + ' port:'))
        self.write('APPL ' + port + ', ' + str(value) + ', 0')

    def getPort(self,port):
        if port == 'P6V':
            return self.P6V
        elif port == 'P25V':
            return self.P25V
        elif port == 'N25V':
            return self.N25V

    def readout(self,times):
        self.t.append(times)
        for port in ['P6V','P25V','N25V']:
            readoutData = float(self.query('APPL? ' + port).strip('"\r\n').split(',')[0])
            self.getPort(port).append(readoutData)

    def plot(self, pause = 0.5):
        recentP6V = self.P6V[-10:]
        recentP25V = self.P25V[-10:]
        recentN25V = self.N25V[-10:]
        recentTime = self.t[-10:]
        plt.figure(1, figsize = (6, 6))
        plt.clf()
        plt.subplot(111)
        plt.plot(recentTime, recentP6V, 'ro', label ='P6V')
        plt.plot(recentTime, recentP25V, 'bo', label ='P25V')
        plt.plot(recentTime, recentN25V, 'go', label ='N25V')
        plt.xlabel('Time')
        plt.xticks(rotation=12, ha = 'right')
        plt.ylabel('Voltage (V)')
        plt.yticks(np.arange(0, 10, 2))
        plt.legend(loc = 'upper right')
        plt.gcf().autofmt_xdate()

        plt.pause(pause)

    def query(self,text):
        return self.resource.query(text)

    def write(self,KeysightCommand):
        self.resource.write(KeysightCommand)

    def terminate(self):
        self.write('*CLS')
        self.write('*RST')
        print(self.query('*IDN?'))
        self.write('SYST:LOC')
        self.resource.close()


'''
------------------------------------------------------------------------------
SIM960 PID
------------------------------------------------------------------------------
'''
class SIM960Class(SIMGenericClass):
    def __init__(self, SIM900, slot):
        SIMGenericClass.__init__(self,SIM900,slot)
        self.presets()

    def presets(self):
        self.P(+1.0E+0)
        self.I(0)
        self.D(0)
        self.Offset(0)
        self.UpperLimit(10)
        self.LowerLimit(0)
        self.Setpoint(3.98,'In')

    def P(self,value):
        if value == '?':
            onOff = self.query('PCTL?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Off', self.query('GAIN?')
            elif onOff == 1:
                return 'On', self.query('GAIN?')
        elif value == 0:
            self.write('PCTL 0')
        else:
            self.write('PCTL 1')
        self.write('GAIN ' + str(value))

    def I(self,value):
        if value == '?':
            onOff = self.query('ICTL?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Off', self.query('INTG?')
            elif onOff == 1:
                return 'On', self.query('INTG?')
        elif value == 0:
            self.write('ICTL 0')
        else:
            self.write('ICTL 1')
        self.write('INTG ' + str(value))

    def D(self,value):
        if value == '?':
            onOff = self.query('DCTL?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Off', self.query('DERV?')
            elif onOff == 1:
                return 'On', self.query('DERV?')
        elif value == 0:
            self.write('DCTL 0')
        else:
            self.write('DCTL 1')
        self.write('DERV ' + str(value))

    def Offset(self,value):
        if value == '?':
            onOff = self.query('OCTL?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Off', self.query('OFST?')
            elif onOff == 1:
                return 'On', self.query('OFST?')
        elif value == 0:
            self.write('OCTL 0')
        else:
            self.write('OCTL 1')
        self.write('OFST ' + str(value))

    def Setpoint(self, value, toggle = 'In'):
        if value == '?':
            intExt = self.query('INPT?')
            intExt = int(intExt.strip('\r\n'))
            if intExt == 1:
                return 'Ex', self.query('SMON? 1')
            elif intExt == 0:
                return 'In', self.query('SMON? 1')
        elif toggle == 'In':
            self.write('INPT 0')
            self.write('SETP ' + str(value))

    def LowerLimit(self,value):
        if value == '?':
           lowerlimit = self.query('LLIM?')
           return lowerlimit
        else:
           self.write('LLIM ' + str(value))
           
    def UpperLimit(self,value):
        if value == '?':
            upperlimit = self.query('ULIM?')
            return upperlimit
        else:
            self.write('ULIM ' + str(value))
    
    def Output(self, value = 0, toggle = 'PID'):
        if value == '?':
            intExt = self.query('AMAN?')
            intExt = int(intExt.strip('\r\n'))
            if intExt == 1:
                return 'PID', self.query('OMON? 1')
            elif intExt == 0:
                return 'Man', self.query('OMON? 1')
        elif toggle == 'PID':
            self.write('AMAN 1')
        elif toggle == 'Man':
            self.write('AMAN 0')
            self.write('MOUT ' + str(value))

    def Measure(self,value = '?'):
        return self.query('MMON? 1')
   
'''
------------------------------------------------------------------------------
SIM921 Resistance Bridge
------------------------------------------------------------------------------
'''
class SIM921Class(SIMGenericClass):
    R = []
    t = []

    def __init__(self, SIM900, slot):
        SIMGenericClass.__init__(self,SIM900,slot)
        #self.presets()

    def presets(self):
        self.Aout(1.0E-1)
        self.Units('Res')
        self.Range('20')
        self.Excite('10u')
        self.TimeConst(0.3)

    def Freq(self,value = '?'):
        if value == '?':
             return self.query('FREQ?')
        else:
             self.write('FREQ ' + str(value))

    def Range(self,value ='?'):
        if value == '?':
             return self.query('RANG?')
        else:
            rangeList = ['20m','200m','2','20','200','2k','20k','200k','2M','20M']
            if type(value) == str:
                index = rangeList.index(value)
                value = index
            self.write('RANG ' + str(value))

    def Excite(self,value= '?'):
        if value == '?':
            onOff = self.query('EXON?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Off', self.query('EXCI?')
            elif onOff == 1:
                return 'On', self.query('EXCI?')
        else:
            exciDict = {'0':-1,'3u':0,'10u':1,'30u':2,'100u':3,'300u':4,'1m':5,\
                        '3m':6,'10m':7,'30m':8}
            if type(value) == str:
                value = exciDict[value]
            if value == -1:
                self.write('EXON 0')
            else:
                self.write('EXON 1')
            self.write('EXCI ' + str(value))

    def R(self,value = '?'):
        if value == '?':
             return self.query('RVAL? 1')
        else:
             self.write('RVAL ' + str(value))

    def Phase(self,value = '?'):
        if value == '?':
             return self.query('PHAS? 1')
        else:
             self.write('PHAS ' + str(value))

    def TimeConst(self,value= '?'):
        if value == '?':
            return self.query('TCON?')
        else:
            value = float(value)
            exciDict = {0:-1,0.3:0,1:1,3:2,10:3,30:4,100:5,300:6}
            value = exciDict[value]
            self.write('TCON ' + str(value))

    def Offset(self,value= '?'):
        if value == '?':
             return self.query('RSET?')
        else:
             self.write('RSET ' + str(value))

    def Aout(self,value= '?'):
        if value == '?':
             return self.query('VOHM?')
        else:
             self.write('VOHM ' + str(value))

    def Units(self,value = '?'):
        if value == '?':
            onOff = self.query('ATEM?')
            onOff = int(onOff.strip('\r\n'))
            if onOff == 0:
                return 'Res'
            elif onOff == 1:
                return 'Temp'
        elif value == 'Res':
            self.write('ATEM ' + str(0))
        elif value == 'Temp':
            self.write('ATEM ' + str(1))

    def readR(self):
        self.mainframe.write('CONN '+ str(self.slot) + ',"slot'+str(self.slot)+'"') # Connect to the slot
        datetime = dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
        rawData = self.mainframe.query('RVAL?1').strip('\r\n').split(',')
        self.mainframe.write('slot'+str(self.slot))
        # Write in a file
        with open('SIM900_' + str(self.mainframe.label) + 'SIM921_' + str(self.slot)+ '.txt', 'a') as f:
            f.write('%s, %f\n' %(datetime,float(rawData[0])))

    def load(self,times,R):
        self.t = times
        self.R = R


def read921(name = 'SIM921_1.txt',last = 10):
    '''
    import os
    with open(name, 'rb') as f:
        f.seek(-2,os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2,os.SEEK_CUR)
        last_line = f.readline().decode()
    '''
    with open(name,'r') as f:
        file = f.readlines()
    if last == -1:
        lines = file
    else:
        lines = file[-last:]
    times = []
    R = []

    for line in lines:
        line = line.strip('\n').split(', ')
        times.append(line[0]+ ' ' + line[1])
        R.append(line[2])

    return times,R

'''
------------------------------------------------------------------------------
SIM925 Multiplexer
------------------------------------------------------------------------------
'''
class SIM925Class(SIMGenericClass):
    def __init__(self, SIM900, slot):
        SIMGenericClass.__init__(self,SIM900,slot)
        self.presets()

    def presets(self):
        self.Channel(0)
        self.Bypass(0)
        self.Buffer(0)

    def Channel(self,value=0):
        if value == '?':
            return self.query('CHAN?')
        else:
            self.write('CHAN ' + str(value))

    def Bypass(self,value=0):
        if value == '?':
            return self.query('BPAS?')
        else:
            self.write('BPAS ' + str(value))

    def Buffer(self,value):
        if value == '?':
            return self.query('BUFR?')
        else:
            self.write('BUFR ' + str(value))

'''
------------------------------------------------------------------------------
E3631 Simple
------------------------------------------------------------------------------
'''
class E3631():

    def readAll(Adr,Channel):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        PS.write('INST:SEL ' + str(Channel))
        while True:
            try:
                V = PS.query('MEAS:VOLT?')
            except pyvisa.errors.VisaIOError:
                print('Read Error')
                continue
            break
        while True:
            try:
                I = PS.query('MEAS:CURR?')
            except pyvisa.errors.VisaIOError:
                print('Read Error')
                continue
            break
        while True:
            try:
                O = PS.query('OUTP?')
            except pyvisa.errors.VisaIOError:
                print('Read Error')
                continue
            break
        return(V,I,O)

    def writeAll(Adr,Channel,Volt,Amp,Output):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        cc = ', '
        PS.write('APPL ' + str(Channel) + cc + str(Volt) + cc + str(Amp))
        PS.write('OUTP ' + str(Output)) 
        X = PS.query('APPL ' + str(Channel) + '?')
        return(X)

    def readV(Adr,Channel):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        PS.write('INST:SEL ' + str(Channel))
        while True:
            try:
                V = PS.query('MEAS:VOLT?')
            except pyvisa.errors.VisaIOError:
                print('Read Error')
                continue
            break
        return(V)
    
    def writeV(Adr,Channel,Volt):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        PS.write('INST:SEL ' + str(Channel))
        PS.write('VOLT ' + str(Volt))
        V = PS.query('MEAS:VOLT?') 
        return(Volt,V)
    
    def readI(Adr,Channel):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        PS.write('INST:SEL ' + str(Channel))
        while True:
            try:
                I = PS.query('MEAS:CURR?')
            except pyvisa.errors.VisaIOError:
                print('Read Error')
                continue
            break 
        return(I)
    
    def writeI(Adr,Channel,Amp):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Channel == 1: Channel = 'P6V'
        if Channel == 2: Channel = 'P25V'
        if Channel == 3: Channel = 'N25V'
        PS.write('INST:SEL ' + str(Channel))
        PS.write('CURR ' + str(Amp))
        I = PS.query('MEAS:CURR?') 
        return(Amp,I)
        
    def Output(Adr,Output):
        rm = pyvisa.ResourceManager()
        PS = rm.open_resource(Adr)
        if Output == '?':
            OutState = PS.query('OUTP?')
        else:
            PS.write('OUTP '+ str(Output))
            OutState = PS.query('OUTP?')
        return(OutState)
