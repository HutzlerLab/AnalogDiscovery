"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
#dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
#  device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in buffer
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) 

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

print("Configuring Digital In...")

nSamples = 100000000 # 100MiB, ~12Mi of 8bit SPI
rgbSamples = (c_uint8*nSamples)()
cAvailable = c_int()
cLost = c_int()
cCorrupted = c_int()
cSamples = 0
fLost = 0
fCorrupted = 0

idxCS = 0
idxClk = 1
idxMosi = 2
idxMiso = 3
nBits = 8

# record mode
dwf.FDwfDigitalInAcquisitionModeSet(hdwf, acqmodeRecord)
# for sync mode set divider to -1 
dwf.FDwfDigitalInDividerSet(hdwf, c_int(-1))
# 8bit per sample format, DIO 0-7
dwf.FDwfDigitalInSampleFormatSet(hdwf, c_int(8))
# continuous sampling 
dwf.FDwfDigitalInTriggerPositionSet(hdwf, c_int(-1))
# in sync mode the trigger is used for sampling condition
# trigger detector mask:          low &     hight & ( rising | falling )
dwf.FDwfDigitalInTriggerSet(hdwf, c_int(0), c_int(0), c_int((1<<idxClk)|(1<<idxCS)), c_int(0))
# sample on clock rising edge for sampling bits, or CS rising edge to detect frames

print("Starting sync record...")
dwf.FDwfDigitalInConfigure(hdwf, c_bool(0), c_bool(1))

try:
    while cSamples < nSamples:
        dwf.FDwfDigitalInStatus(hdwf, c_int(1), byref(sts))

        dwf.FDwfDigitalInStatusRecord(hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))

        cSamples += cLost.value
        
        if cLost.value :
            fLost = 1
        if cCorrupted.value :
            fCorrupted = 1

        if cAvailable.value!=0 :
            if cSamples+cAvailable.value > nSamples :
                cAvailable = c_int(nSamples-cSamples)
            # get samples
            dwf.FDwfDigitalInStatusData(hdwf, byref(rgbSamples, cSamples), c_int(cAvailable.value))
            cSamples += cAvailable.value
        
        if sts != DwfStateRunning :
            continue

except KeyboardInterrupt: # Ctrl+C
    pass

dwf.FDwfDeviceClose(hdwf)

print("   done", str(cSamples), "samples")
if fLost:
    print("Samples were lost!")
elif cCorrupted:
    print("Samples could be corrupted!")

print("Decoding data and saving to file")

fsMosi = 0
fsMiso = 0
cBit = 0

fMosi = open("record_mosi.csv", "w")
fMiso = open("record_miso.csv", "w")

for i in range(0,cSamples):
    v = rgbSamples[i]
    if (v>>idxCS)&1: # CS high, inactive
        if cBit != 0: # log leftover bits, frame not multiple of nBits
            fMosi.write("X%s %s " % (cBit, hex(fsMosi)))
            fMiso.write("X%s %s " % (cBit, hex(fsMiso)))
        cBit = 0
        fsMosi = 0
        fsMiso = 0
        fMosi.write("\n")
        fMiso.write("\n")
    else:
        cBit+=1
        fsMosi <<= 1 # MSB first
        fsMiso <<= 1 # MSB first
        if (v>>idxMosi)&1 :
            fsMosi |= 1
        if (v>>idxMiso)&1 :
            fsMiso |= 1
        if cBit >= nBits: # got nBits of bits
            fMosi.write("%s " % hex(fsMosi))
            fMiso.write("%s " % hex(fsMiso))
            cBit = 0
            fsMosi = 0
            fsMiso = 0
fMosi.close()
fMiso.close()




