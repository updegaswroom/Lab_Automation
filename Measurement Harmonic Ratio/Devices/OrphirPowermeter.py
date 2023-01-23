# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
# Uses pywin32
import win32com.client
import time
import traceback


def measure(setAverage, setRange, silent):
    if not silent:
        print(setRange)
        #(Ranges - corresp ID: ('AUTO' - 0, '2.00W' - 1, '300mW' - 2, '30.0mW' - 3, '3.00mW' - 4))

    Range_Limits = [2 , 2, 0.2, 0.02, 0.002, 0]
    Range_waittime = [.2, .2, .2, .25, .3]
    Counter = 0
    powers = 0
    status = False
    try:
     OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
     # Stop & Close all devices
     OphirCOM.StopAllStreams() 
     OphirCOM.CloseAll()
     # Scan for connected Devices
     DeviceList = OphirCOM.ScanUSB()
     #print(DeviceList)
     for Device in DeviceList:   	# if any device is connected
      DeviceHandle = OphirCOM.OpenUSBDevice(Device)	# open first device
      exists = OphirCOM.IsSensorExists(DeviceHandle, 0)
      if exists:
       #print('\n----------Data for S/N {0} ---------------'.format(Device))
       # An Example for Range control. first get the ranges
       #ranges = OphirCOM.GetRanges(DeviceHandle, 0)

       OphirCOM.SetRange(DeviceHandle, 0, setRange) #set new Range
       time.sleep(1) #wait a little bit just to make sure range is set properly
       OphirCOM.StartStream(DeviceHandle, 0)# start measuring, flushes buffer from previous measurement

       for i in range(setAverage):		
        time.sleep(Range_waittime[setRange])	# wait a little for data
        data = OphirCOM.GetData(DeviceHandle, 0)
        if len(data[0]) > 0:		# if any data available, print the first one from the batch
         if not silent:
            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
         if (data[0][0] <= 0 or data[0][0] < Range_Limits[setRange+1]) :
            status = True
         powers = powers + data[0][0]
         Counter = Counter + 1
        # Status: 0 - OK 1 - Overrange 2 - Saturated --> check what this means in detail
        #return oversaturated -- repeat if thats the case
      else:
       print('\nNo Sensor attached to {0} !!!'.format(Device))
    except OSError as err:
     print("OS error: {0}".format(err))
    except:
     traceback.print_exc()

    # Stop & Close all devices
    OphirCOM.StopAllStreams()
    OphirCOM.CloseAll()
    # Release the object
    OphirCOM = None

    Power = round(powers/Counter,5)
    return Power, status, data[2][0]

def getPower_auto(Average = None, Range = None, silent = True):

    if Average == None:
        setAverage = 10
    elif Average >= 1 and Average <= 50:
        setAverage = Average
    else:
        print('invalid average')

    if Range == None:
        setRange = 2
    elif Range >=0 and Range <=4:
        setRange = Range
    else:
        print('invalid PM range')

    Power, RangeStatus, SatStatus = measure(setAverage, setRange, silent)
    while RangeStatus and setRange <4:
        setRange = setRange + 1
        Power, RangeStatus, SatStatus = measure(setAverage, setRange, silent)
    
    if SatStatus == 2:
        setRange = 2
        Power, RangeStatus, SatStatus = measure(setAverage, setRange, silent)
    if not silent:
        print(Power)
    return Power

def getPower():
    setAverage = 10
    setRange = 2

    Power = measure(setAverage, setRange)

    #print(Power)
    return Power
    
if __name__ == "__main__":
    #getPower()
    getPower_auto()