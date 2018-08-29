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

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# check library loading errors
szerr = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))

# declare variables
IsInUse = c_bool()
hdwf = c_int()
int0 = c_int()
int1 = c_int()
uint0 = c_uint()
dbl0 = c_double()
dbl1 = c_double()
dbl2 = c_double()
sz0 = create_string_buffer(256)
sz1 = create_string_buffer(256)
cDevice = c_int()
cChannel = c_int()
cNode = c_int()
rgszAnalogOutNode = ["Carrier", "FM", "AM"]

# declare string variables
devicename = create_string_buffer(64)
serialnum = create_string_buffer(16)

# print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# enumerate connected devices
dwf.FDwfEnum(c_int(0), byref(cDevice))
print("Number of Devices: "+str(cDevice.value))

# open devices
for iDevice in range(0, cDevice.value):
    dwf.FDwfEnumDeviceName(c_int(iDevice), devicename)
    dwf.FDwfEnumSN(c_int(iDevice), serialnum)
    print("------------------------------")
    print("Device "+str(iDevice+1)+" : ")
    print("\t" + str(devicename.value))
    print("\t" + str(serialnum.value))
    dwf.FDwfDeviceOpen(c_int(iDevice), byref(hdwf))
    if hdwf.value == 0:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(szerr.value)
        continue
    
    print("")
    dwf.FDwfAnalogInChannelCount(hdwf, byref(int0))
    print("AnalogIn channels: "+str(int0.value))

    dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, byref(int0))
    print("Buffer size: "+str(int0.value))

    dwf.FDwfAnalogInBitsInfo(hdwf, byref(int0))
    print("ADC bits: "+str(int0.value))

    dwf.FDwfAnalogInChannelRangeInfo(hdwf, byref(dbl0), byref(dbl1), byref(dbl2))
    print("Range from "+str(dbl0.value)+" to "+str(dbl1.value)+" in "+str(dbl2.value)+" steps")

    dwf.FDwfAnalogInChannelOffsetInfo(hdwf, byref(dbl0), byref(dbl1), byref(dbl2))
    print("Offset from "+str(dbl0.value)+" to "+str(dbl1.value)+" in "+str(dbl2.value)+" steps")

    
    print("")
    dwf.FDwfAnalogOutCount(hdwf, byref(cChannel))
    print("AnalogOut channels: "+str(cChannel.value))
    
    for iChannel in range(0, cChannel.value):
        print("Channel "+str(iChannel+1))

        fsnodes = c_int()
        dwf.FDwfAnalogOutNodeInfo(hdwf, c_int(iChannel), byref(fsnodes))

        for iNode in range(0, 2):
            if (fsnodes.value & (1<<iNode)) == 0:  # bits: AM | FM | Carrier
                continue
                
            print("Node: "+rgszAnalogOutNode[iNode])

            dwf.FDwfAnalogOutNodeDataInfo(hdwf, iChannel, iNode, 0, byref(int0))
            print("Buffer size: "+str(int0.value))
            
            dwf.FDwfAnalogOutNodeAmplitudeInfo(hdwf, iChannel, iNode, byref(dbl0), byref(dbl1))
            print("Amplitude from "+str(dbl0.value)+" to "+str(dbl1.value))

            dwf.FDwfAnalogOutNodeOffsetInfo(hdwf, iChannel, iNode, byref(dbl0), byref(dbl1))
            print("Offset from "+str(dbl0.value)+" to "+str(dbl1.value))

            dwf.FDwfAnalogOutNodeFrequencyInfo(hdwf, iChannel, iNode, byref(dbl0), byref(dbl1))
            print("Frequency from "+str(dbl0.value)+" to "+str(dbl1.value))

    print("")
    dwf.FDwfAnalogIOChannelCount(hdwf, byref(cChannel))
    print("AnalogIO channels: "+str(cChannel.value))

    dwf.FDwfAnalogIOEnableInfo(hdwf, byref(int0), byref(int1))
    print("Master Enable: "+("Setting " if int0!=0 else "")+("Reading " if int1!=0 else ""))

    for iChannel in range(0, cChannel.value):

        dwf.FDwfAnalogIOChannelName(hdwf, iChannel, sz0, sz1)
        print("Channel "+str(iChannel+1)+" Name: \""+str(sz0.value)+"\" Label: \""+str(sz1.value)+"\"")

        dwf.FDwfAnalogIOChannelInfo(hdwf, iChannel, byref(cNode))
        
        for iNode in range(0, cNode.value):
            dwf.FDwfAnalogIOChannelNodeName(hdwf, iChannel, iNode, sz0, sz1)
            print("Node "+str(iNode+1)+" Name: \""+str(sz0.value)+"\" Unit: \""+str(sz1.value)+"\"")

            dwf.FDwfAnalogIOChannelNodeSetInfo(hdwf, iChannel, iNode, byref(dbl0), byref(dbl1), byref(int0))
            if int0.value==1 :
                if dbl0.value == dbl1.value  :
                    print("Constant output "+str(dbl0.value))
                else:
                    print("Non settable range from "+str(dbl0)+" to "+str(dbl1))
            elif int0.value>1 :
                print("Setting from "+str(dbl0.value)+" to "+str(dbl1.value)+" in "+str(int0.value)+" steps")

            dwf.FDwfAnalogIOChannelNodeStatusInfo(hdwf, iChannel, iNode, byref(dbl0), byref(dbl1), byref(int0))
            if int0.value==1 :
                if dbl0.value == dbl1.value  :
                    print("Constant input "+str(dbl0.value))
                else:
                    print("Input range from "+str(dbl0.value)+" to "+str(dbl1.value))
            elif int0.value>1 :
                print("Reading from "+str(dbl0.value)+" to "+str(dbl1.value)+" in "+str(int0.value)+" steps")

                
    print("")
    dwf.FDwfDigitalInBitsInfo(hdwf, byref(int0))
    print("DigitalIn channels: "+str(int0.value))

    dwf.FDwfDigitalInBufferSizeInfo(hdwf, byref(int0))
    print("Buffer size: "+str(int0.value))

    
    print("")
    dwf.FDwfDigitalOutCount(hdwf, byref(int0))
    print("DigitalOut channels: "+str(int0.value))

    dwf.FDwfDigitalOutDataInfo(hdwf, c_int(0), byref(int0))
    print("Custom size: "+str(int0.value))

    
    print("")
    print("DigitalIO information:")
    dwf.FDwfDigitalIOOutputEnableInfo(hdwf, byref(uint0))
    print("OE Mask: "+hex(uint0.value))
    dwf.FDwfDigitalIOOutputInfo(hdwf, byref(uint0))
    print("Output : "+hex(uint0.value))
    dwf.FDwfDigitalIOInputInfo(hdwf, byref(uint0))
    print("Input  : "+hex(uint0.value))

# ensure all devices are closed
dwf.FDwfDeviceCloseAll()
