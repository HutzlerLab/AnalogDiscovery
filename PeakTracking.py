# Written by Arian Jadbabaie with help from Digilent code
from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy as np

parameters = {
	'Num Samples'	:8192,
	#preferably 2^n
	'Ramp Freq'		:50,
	#Hz
	'Trig Delay'	:0.5,
}

def monitorPeaks():
	initialize(parameters)
	dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))
	while True:
		try:
		acquire()
		fit()
		plot()
	except KeyboardInterrupt:
		save()
		close()


def initialize():
	if sys.platform.startswith("win"):
		dwf = cdll.dwf
	elif sys.platform.startswith("darwin"):
		dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
	else:
		dwf = cdll.LoadLibrary("libdwf.so")
	hdwf = c_int()
	sts = c_byte()
	samples = parameters['Num Samples']
	rgdSamples = (c_double*samples)()
	length = 1/parameters['Ramp Freq']
	length = length*(0.995)
	freq = samples/length
	trig_delay = parameters['Trig Delay']
	version = create_string_buffer(16)
	dwf.FDwfGetVersion(version)
	print("DWF Version: "+str(version.value))
	print("Opening first device")
	dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
	if hdwf.value == hdwfNone.value:
		szError = create_string_buffer(512)
		dwf.FDwfGetLastErrorMsg(szError);
		print("failed to open device\n"+str(szError.value))
		quit()

	#Acquisition setup
	dwf.FDwfAnalogInFrequencySet(hdwf, c_double(freq))
	dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(samples)) 
	dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
	dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(2))

	#set up trigger
	dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(10)) # 10 second auto trigger timeout
	dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcExternal1) 
	dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
	dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0.5)) # 0.5V
	dwf.FDwfAnalogInTriggerConditionSet(hdwf, trigcondRisingPositive) 
	dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(-trig_delay*length))
	time.sleep(2)

def acquire():
	while True:
		dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
		if sts.value == DwfStateDone.value :
			break
	dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 8192)