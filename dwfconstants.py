"""
   DWFConstants (definitions file for DWF library)
   Author:  Digilent, Inc.
   Revision:  2018-07-31

   Must install:                       
       Python 2.7 or 3
"""

from ctypes import *

#HDWF
hdwfNone = c_int(0)

#ENUMFILTER
enumfilterAll       = c_int(0)
enumfilterEExplorer = c_int(1)
enumfilterDiscovery = c_int(2)

#DEVID
devidEExplorer  = c_int(1)
devidDiscovery  = c_int(2)

#DEVVER
devverEExplorerC   = c_int(2)
devverEExplorerE   = c_int(4)
devverEExplorerF   = c_int(5)
devverDiscoveryA   = c_int(1)
devverDiscoveryB   = c_int(2)
devverDiscoveryC   = c_int(3)

#TRIGSRC
trigsrcNone                 = c_ubyte(0)
trigsrcPC                   = c_ubyte(1)
trigsrcDetectorAnalogIn     = c_ubyte(2)
trigsrcDetectorDigitalIn    = c_ubyte(3)
trigsrcAnalogIn             = c_ubyte(4)
trigsrcDigitalIn            = c_ubyte(5)
trigsrcDigitalOut           = c_ubyte(6)
trigsrcAnalogOut1           = c_ubyte(7)
trigsrcAnalogOut2           = c_ubyte(8)
trigsrcAnalogOut3           = c_ubyte(9)
trigsrcAnalogOut4           = c_ubyte(10)
trigsrcExternal1            = c_ubyte(11)
trigsrcExternal2            = c_ubyte(12)
trigsrcExternal3            = c_ubyte(13)
trigsrcExternal4            = c_ubyte(14)

# instrument states
DwfStateReady        = c_ubyte(0)
DwfStateConfig       = c_ubyte(4)
DwfStatePrefill      = c_ubyte(5)
DwfStateArmed        = c_ubyte(1)
DwfStateWait         = c_ubyte(7)
DwfStateTriggered    = c_ubyte(3)
DwfStateRunning      = c_ubyte(3)
DwfStateDone         = c_ubyte(2)

#STS
stsRdy		= c_ubyte(0)
stsArm		= c_ubyte(1)
stsDone		= c_ubyte(2)
stsTrig		= c_ubyte(3)
stsCfg		= c_ubyte(4)
stsPrefill	= c_ubyte(5)
stsNotDone	= c_ubyte(6)
stsTrigDly	= c_ubyte(7)
stsError	= c_ubyte(8)
stsBusy		= c_ubyte(9)
stsStop		= c_ubyte(10)

#ACQMODE
acqmodeSingle       = c_int(0)
acqmodeScanShift    = c_int(1)
acqmodeScanScreen   = c_int(2)
acqmodeRecord       = c_int(3)

#FILTER
filterDecimate = c_int(0)
filterAverage  = c_int(1)
filterMinMax   = c_int(2)

#TRIGTYPE
trigtypeEdge         = c_int(0)
trigtypePulse        = c_int(1)
trigtypeTransition   = c_int(2)

#TRIGCOND
trigcondRisingPositive   = c_int(0)
trigcondFallingNegative  = c_int(1)

#TRIGLEN;
triglenLess       = c_int(0)
triglenTimeout    = c_int(1)
triglenMore       = c_int(2)

#DWFERC;                           
dwfercNoErc                  = c_int(0)		#  No error occurred
dwfercUnknownError           = c_int(1)		#  API waiting on pending API timed out
dwfercApiLockTimeout         = c_int(2)		#  API waiting on pending API timed out
dwfercAlreadyOpened          = c_int(3)		#  Device already opened
dwfercNotSupported           = c_int(4)		#  Device not supported
dwfercInvalidParameter0      = c_int(16)	#  Invalid parameter sent in API call
dwfercInvalidParameter1      = c_int(17)	#  Invalid parameter sent in API call
dwfercInvalidParameter2      = c_int(18)	#  Invalid parameter sent in API call
dwfercInvalidParameter3      = c_int(19)	#  Invalid parameter sent in API call

#FUNC;
funcDC       = c_ubyte(0)
funcSine     = c_ubyte(1)
funcSquare   = c_ubyte(2)
funcTriangle = c_ubyte(3)
funcRampUp   = c_ubyte(4)
funcRampDown = c_ubyte(5)
funcNoise    = c_ubyte(6)
funcCustom   = c_ubyte(30)
funcPlay     = c_ubyte(31)

#ANALOGIO;
analogioEnable      = c_ubyte(1)
analogioVoltage     = c_ubyte(2)
analogioCurrent     = c_ubyte(3)
analogioPower       = c_ubyte(4)
analogioTemperature	= c_ubyte(5)

AnalogOutNodeCarrier  = c_int(0)
AnalogOutNodeFM       = c_int(1)
AnalogOutNodeAM       = c_int(2)

DwfDigitalInClockSourceInternal = c_int(0)
DwfDigitalInClockSourceExternal = c_int(1)

DwfDigitalInSampleModeSimple   = c_int(0)
# alternate samples: noise|sample|noise|sample|...  
# where noise is more than 1 transition between 2 samples
DwfDigitalInSampleModeNoise    = c_int(1)

DwfDigitalOutOutputPushPull   = c_int(0)
DwfDigitalOutOutputOpenDrain  = c_int(1)
DwfDigitalOutOutputOpenSource = c_int(2)
DwfDigitalOutOutputThreeState = c_int(3) 

DwfDigitalOutTypePulse      = c_int(0)
DwfDigitalOutTypeCustom     = c_int(1)
DwfDigitalOutTypeRandom     = c_int(2)
DwfDigitalOutTypeROM        = c_int(3)

DwfDigitalOutIdleInit     = c_int(0)
DwfDigitalOutIdleLow      = c_int(1)
DwfDigitalOutIdleHigh     = c_int(2)
DwfDigitalOutIdleZet      = c_int(3)

DwfAnalogImpedanceImpedance = c_int(0)
DwfAnalogImpedanceImpedancePhase = c_int(1)
DwfAnalogImpedanceResistance = c_int(2)
DwfAnalogImpedanceReactance = c_int(3)
DwfAnalogImpedanceAdmittance = c_int(4)
DwfAnalogImpedanceAdmittancePhase = c_int(5)
DwfAnalogImpedanceConductance = c_int(6)
DwfAnalogImpedanceSusceptance = c_int(7)
DwfAnalogImpedanceSeriesCapactance = c_int(8)
DwfAnalogImpedanceParallelCapacitance = c_int(9)
DwfAnalogImpedanceSeriesInductance = c_int(10)
DwfAnalogImpedanceParallelInductance = c_int(11)
DwfAnalogImpedanceDissipation = c_int(12)
DwfAnalogImpedanceQuality = c_int(13)

DwfParamKeepOnClose = c_int(1)
DwfParamKeepUsbOn = c_int(2)

