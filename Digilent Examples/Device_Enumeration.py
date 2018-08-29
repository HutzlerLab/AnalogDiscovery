"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#check library loading errors
szerr = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))

#declare ctype variables
IsInUse = c_bool()
hdwf = c_int()
cDevice = c_int()
cConfig = c_int()
cInfo = c_int()

#declare string variables
devicename = create_string_buffer(64)
serialnum = create_string_buffer(16)

#print DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#enumerate and print device information
dwf.FDwfEnum(c_int(0), byref(cDevice))
print("Number of Devices: "+str(cDevice.value))

for iDev in range(0, cDevice.value):
    dwf.FDwfEnumDeviceName (c_int(iDev), devicename)
    dwf.FDwfEnumSN (c_int(iDev), serialnum)
    print("------------------------------")
    print("Device "+str(iDev)+" : ")
    print("\tName:\'" + str(devicename.value) + "' " + str(serialnum.value))

    print("\tConfigurations:")
    dwf.FDwfEnumConfig(c_int(iDev), byref(cConfig))
    for iCfg in range (0, cConfig.value):
        sz = "\t"+str(iCfg)+"."
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(1), byref(cInfo)) # DECIAnalogInChannelCount
        sz += " AnalogIn: "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(7), byref(cInfo)) # DECIAnalogInBufferSize
        sz += " x "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(2), byref(cInfo)) # DECIAnalogOutChannelCount
        sz += " \tAnalogOut: "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(8), byref(cInfo)) # DECIAnalogOutBufferSize
        sz += " x "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(4), byref(cInfo)) # DECIDigitalInChannelCount
        sz += " \tDigitalIn: "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(9), byref(cInfo)) # DECIDigitalInBufferSize
        sz += " x "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(5), byref(cInfo)) # DECIDigitalOutChannelCount
        sz += " \tDigitalOut: "+str(cInfo.value)
        dwf.FDwfEnumConfigInfo(c_int(iCfg), c_int(10), byref(cInfo)) # DECIDigitalOutBufferSize
        sz += " x "+str(cInfo.value)
        print(sz)
