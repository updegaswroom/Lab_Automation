import tkinter as tk
import PumpProbe_GUI_class as tkgui

import Devices.TOPAS4OrpheusF_NET_SDK as opa										#OPA	
from seabreeze.spectrometers import list_devices, Spectrometer			
import Devices.MM4006 as delaystage												#Controler of the delaystage


serialNumberTopas = "P18273"
comportStage = "COM2"

TOPAS = opa.Topas4OrpheusF(serialNumberTopas)
TOPAS.closeShutter()

SPECTROMETER = Spectrometer.from_first_available()
inttime = 100000
if int(inttime) < max(SPECTROMETER.integration_time_micros_limits):
	SPECTROMETER.integration_time_micros(int(inttime))


CONTROLER = delaystage.NewportMM4006(comportStage)	
CONTROLER = delaystage.NewportMM4006(comportStage)								#Connect to Controler
DELAYSTAGE = delaystage.Axis(CONTROLER, 3)													#Connect to Delaystage, located at axis 4 (i.e. controlunit 4)
DELAYSTAGE.unit()															#get information of the displacement unit
DELAYSTAGE.motor_on()	

root = tk.Tk()
gui = tkgui.GUI(root, TOPAS, SPECTROMETER, DELAYSTAGE)
gui.setup()

root.mainloop()