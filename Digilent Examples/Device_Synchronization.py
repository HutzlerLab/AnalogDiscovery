"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-24

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys
import time
import matplotlib.pyplot as plt
import numpy as np

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

szerr = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))

IsInUse = c_bool()
hdwf = c_int()
rghdwf = []
cChannel = c_int()
cDevice = c_int()
sts = c_byte()
cSamples = 8192
rgdSamples = (c_double*cSamples)()

devicename = create_string_buffer(32)
serialnum = create_string_buffer(32)

version = create_string_buffer(32)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# enumerate connected devices
dwf.FDwfEnum(c_int(0), byref(cDevice))
print("Number of Devices: "+str(cDevice.value))

# open devices
for idevice in range(0, cDevice.value):
    dwf.FDwfEnumDeviceName(c_int(idevice), devicename)
    dwf.FDwfEnumSN(c_int(idevice), serialnum)
    print("------------------------------")
    print("Device "+str(idevice+1)+" : ")
    print("\t" + str(devicename.value))
    print("\t" + str(serialnum.value))
    
    dwf.FDwfDeviceOpen(c_int(idevice), byref(hdwf))
    if hdwf.value == 0:
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        dwf.FDwfDeviceCloseAll()
        sys.exit(0)
        
    rghdwf.append(hdwf.value)
    
    if idevice == 0:
        # on first device drive External T1 (0) with trigsrcPC (1) 
        # expects T1 of each device to be connected together for synchronization
        dwf.FDwfDeviceTriggerSet(hdwf, c_int(0), c_int(1)) # 1 = trigsrcPC
        print("Generating sine wave...")
        dwf.FDwfAnalogOutTriggerSourceSet(hdwf, c_int(0), c_int(11)) # 11 = trigsrcExternal1
        dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), c_int(1))
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(1e3))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(2))
        dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(True))


    dwf.FDwfAnalogInTriggerSourceSet(hdwf, c_int(11)) # 11 = trigsrcExternal1
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(1e6))
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1)) 

# wait at least 2 seconds with Analog Discovery for the offset to stabilize, before the first reading after device open or offset/range change
time.sleep(2)

 
# wait for the last configured device to armed too
hdwf.value = rghdwf[cDevice.value-1]
while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(0), byref(sts))
    if sts.value == 1 : # DwfStateArmed
        break

# generate trigger signal
hdwf.value = rghdwf[0]
dwf.FDwfDeviceTriggerPC(hdwf)

# wait for acquisition to be done
while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(0), byref(sts))
    if sts.value == 2 : # DwfStateDone
        break

plt.figure(1)
for iDevice in range(0, cDevice.value):
    hdwf.value = rghdwf[iDevice]
    print("Device " + str(iDevice+1))
    
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if sts.value != 2 : # DwfStateDone
        print("Not triggered!")
        continue
    
    # get data of each channel
    dwf.FDwfAnalogInChannelCount(hdwf, byref(cChannel))
    for iChannel in range(0, cChannel.value):
        dwf.FDwfAnalogInStatusData(hdwf, iChannel, rgdSamples, c_int(cSamples))
        print("Average on Channel " + str(iChannel+1)+" : "+ str(sum(rgdSamples)/cSamples)+"V")
        plt.plot(np.fromiter(rgdSamples, dtype = np.float))

plt.show()
# ensure all devices are closed
dwf.FDwfDeviceCloseAll()
