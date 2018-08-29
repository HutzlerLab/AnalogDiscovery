"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import time
import matplotlib.pyplot as plt
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()
cSamples = 4000
rgdAnalog = (c_double*cSamples)()
rgwDigital = (c_uint16*cSamples)()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()


print("Generating signal on DIO 0")
# generate on DIO-0 25khz pulse (100MHz/10000/(7+3)), 30% duty (7low 3high)
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(0), c_int(100))
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(0), c_int(7), c_int(3))
dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))


# For synchronous analog/digital acquisition set DigitalInTriggerSource to AnalogIn, start DigitalIn then AnalogIn

# configure DigitalIn
dwf.FDwfDigitalInTriggerSourceSet(hdwf, c_ubyte(4)) # trigsrcAnalogIn
#sample rate = system frequency / divider, 100MHz/1
dwf.FDwfDigitalInDividerSet(hdwf, c_int(1))
# 16bit per sample format
dwf.FDwfDigitalInSampleFormatSet(hdwf, c_int(16))
# set number of sample to acquire
dwf.FDwfDigitalInBufferSizeSet(hdwf, c_int(cSamples))
dwf.FDwfDigitalInTriggerPositionSet(hdwf, c_int(int(cSamples/2))) # trigger position in middle of buffer

# configure AnalogIn
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(1e8))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(cSamples)) 
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(0)) # trigger position in middle of buffer
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(0), c_double(-2.0))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5.0))

#trigger on digital signal
#dwf.FDwfAnalogInTriggerSourceSet(hdwf, c_byte(3)) # trigsrcDetectorDigitalIn
#dwf.FDwfDigitalInTriggerSet(hdwf, c_int(0), c_int(0), c_int(1), c_int(0)) # DIO-0 rising edge

# trigger on analog signal
dwf.FDwfAnalogInTriggerSourceSet(hdwf, c_byte(2)) # trigsrcDetectorAnalogIn
dwf.FDwfAnalogInTriggerTypeSet(hdwf, c_int(0)) # trigtypeEdge
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # first channel
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(1.5)) # 1.5V
dwf.FDwfAnalogInTriggerConditionSet(hdwf, c_int(0))  # trigcondRisingPositive

#wait at least 2 seconds for the offset to stabilize
time.sleep(2)

# start DigitalIn and AnalogIn
dwf.FDwfDigitalInConfigure(hdwf, c_int(True), c_int(True))
dwf.FDwfAnalogInConfigure(hdwf, c_int(True), c_int(True))

while True: # wait to be armed
  dwf.FDwfDigitalInStatus(hdwf, c_int(0), byref(sts))
  print("DigitalIn state: "+str(sts.value))
  if sts.value == 5 :
    continue
  dwf.FDwfAnalogInStatus(hdwf, c_int(0), byref(sts))
  print("AnalogIn state: "+str(sts.value))
  if sts.value == 5 :
    continue
  break
  
while True:
    time.sleep(1)
    dwf.FDwfDigitalInStatus(hdwf, c_int(1), byref(sts))
    if sts.value == 2 : # done
       dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
       break

# read data
dwf.FDwfDigitalInStatusData(hdwf, rgwDigital, c_int(sizeof(c_uint16)*cSamples)) 
dwf.FDwfAnalogInStatusData(hdwf, c_int(0), rgdAnalog, c_int(cSamples)) # get channel 1 data
#dwf.FDwfAnalogInStatusData(hdwf, 1, rgdAnalog, cSamples) # get channel 2 data


dwf.FDwfDigitalOutReset(hdwf)
dwf.FDwfDeviceCloseAll()

# plot
rgIndex=[0.0]*(cSamples)
rgAnalog=[0.0]*(cSamples)
rgDigital=[0.0]*(cSamples)
for i in range(0,cSamples):
    rgIndex[i]=i
    rgAnalog[i]=rgdAnalog[i]
    rgDigital[i]=rgwDigital[i]&1 # mask DIO0

plt.plot(rgIndex, rgAnalog, rgIndex, rgDigital)
plt.show()


