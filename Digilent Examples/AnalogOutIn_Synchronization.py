"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys
import time
import matplotlib.pyplot as plt
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

IsInUse = c_bool()
hdwf = c_int()
rghdwf = []
cChannel = c_int()
cDevices = c_int()
voltage = c_double();
sts = c_byte()
cSamples = 8192
rgdSamples = (c_double*cSamples)()

# declare string variables
devicename = create_string_buffer(64)
serialnum = create_string_buffer(16)

# print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# enumerate connected devices
dwf.FDwfEnum(c_int(0), byref(cDevices))
if cDevices.value == 0:
    print("No device found")
    dwf.FDwfDeviceCloseAll()
    sys.exit(0)
    
print("Number of Devices: "+str(cDevices.value))

# open devices
for iDevice in range(0, cDevices.value):
    dwf.FDwfEnumDeviceName(c_int(iDevice), devicename)
    dwf.FDwfEnumSN(c_int(iDevice), serialnum)
    print("------------------------------")
    print("Device "+str(iDevice+1)+" : \t" + str(devicename.value) + "\t" + str(serialnum.value))
    dwf.FDwfDeviceOpen(c_int(iDevice), byref(hdwf))
    if hdwf.value == 0:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        dwf.FDwfDeviceCloseAll()
        sys.exit(0)
        
    rghdwf.append(hdwf.value)
        
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(1e8))
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(-1), c_int(1)) 
    dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(-1), c_double(0)) 
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(5)) 
    dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(cSamples*4/10/1e8)) # 0 is middle, 4/10 = 10%
    # trigger source external trigger 1
    dwf.FDwfAnalogInTriggerSourceSet(hdwf, c_byte(11)) # 11 = trigsrcExternal1, T1
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0)) 

    if iDevice == 0:
        # trigger output on external trigger 2 of analog-out (AWG) 1 
        dwf.FDwfDeviceTriggerSet(hdwf, c_int(0), c_byte(7)) # 0 = T1 , 7 = trigsrcAnalogOut1
        dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), c_byte(1)) # funcSine
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(5e4))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(1.5))
        dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(0), c_int(0), c_double(0))

# wait at least 2 seconds for the device offset to stabilize
time.sleep(2)

# start analog-in (Scope)
for iDevice in range(len(rghdwf)):
    hdwf.value = rghdwf[iDevice]
    dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

print("This example expects Trigger 1 of each device to be connected together for synchronization triggering!")
for iAcq in range(0, 1):
    hdwf.value = rghdwf[0]
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1)) # start analog-out (AWG) 1 of first device
    
    for iDevice in range(len(rghdwf)):
        hdwf.value = rghdwf[iDevice]
        while True:
            dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
            if sts.value == 2 : # DwfStateDone
                break
            time.sleep(0.1)
        
        dwf.FDwfAnalogInChannelCount(hdwf, byref(cChannel)) 
        for iChannel in range(0, cChannel.value):
            dwf.FDwfAnalogInStatusData(hdwf, c_int(iChannel), rgdSamples, c_int(cSamples)) # get channel 1 data

            plt.plot(numpy.fromiter(rgdSamples, dtype = numpy.float))
            
    plt.show()

dwf.FDwfDeviceCloseAll()
