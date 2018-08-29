"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
sts = c_byte()
hzAcq = c_double(100000)
nSamples = 200000
rgdSamples = (c_double*nSamples)()
cAvailable = c_int()
cLost = c_int()
cCorrupted = c_int()
fLost = 0
fCorrupted = 0

#print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

print("Generating sine wave...")
#                                    AWG 1     carrier
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), funcSine)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(1))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(2))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(True))

#set up acquisition
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, c_int(3)) # record
dwf.FDwfAnalogInFrequencySet(hdwf, hzAcq)
sRecord = nSamples/hzAcq.value
dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(sRecord)) # -1 infinite record length
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(-0.25*sRecord)) # -0.25 = trigger at 25%

#set up trigger
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(10)) # 10 second auto trigger timeout
dwf.FDwfAnalogInTriggerSourceSet(hdwf, c_ubyte(2)) # trigsrcDetectorAnalogIn
dwf.FDwfAnalogInTriggerTypeSet(hdwf, c_int(0)) # trigtypeEdge
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # channel 1
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0)) # 0V
dwf.FDwfAnalogInTriggerHysteresisSet(hdwf, c_double(0.01)) # 0.01V
dwf.FDwfAnalogInTriggerConditionSet(hdwf, c_int(0)) # trigcondRisingPositive 

#wait at least 2 seconds for the offset to stabilize
time.sleep(2)

print("Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

iSample = 0

while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    dwf.FDwfAnalogInStatusRecord(hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))
    #print(str(iSample),str(sts.value),str(cAvailable.value))
    iSample += cLost.value
    iSample %= nSamples

    if cLost.value :
        fLost = 1
    if cCorrupted.value :
        fCorrupted = 1

    iBuffer = 0
    while cAvailable.value>0:
        cSamples = cAvailable.value
        # we are using circular sample buffer, make sure to not overflow
        if iSample+cAvailable.value > nSamples:
            cSamples = nSamples-iSample
        dwf.FDwfAnalogInStatusData2(hdwf, c_int(0), byref(rgdSamples, sizeof(c_double)*iSample), c_int(iBuffer), c_int(cSamples)) # get channel 1 data
        #dwf.FDwfAnalogInStatusData2(hdwf, c_int(1), byref(rgdSamples2, sizeof(c_double)*iSample), c_int(iBuffer), c_int(cSamples)) # get channel 2 data
        iBuffer += cSamples
        cAvailable.value -= cSamples
        iSample += cSamples
        iSample %= nSamples

    if sts.value == 2 : # done
        break

dwf.FDwfAnalogOutReset(hdwf, c_int(0))
dwf.FDwfDeviceCloseAll()

print("Recording done")
if fLost:
    print("Samples were lost! Reduce frequency")
if fCorrupted:
    print("Samples could be corrupted! Reduce frequency")

f = open("record.csv", "w")
for i in range(0, nSamples):
    f.write("%s\n" % rgdSamples[(i+iSample)%nSamples]) # first sample in our buffer is at iSample index
f.close()
  
plt.plot(numpy.fromiter(rgdSamples, dtype = numpy.float))
plt.show()


