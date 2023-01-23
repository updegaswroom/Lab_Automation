import tkinter as tk
import HarmonicRatio_GUI_class as tkgui

import Devices.TOPAS4OrpheusF_NET_SDK as opa										#OPA	
import Devices.smc100 as rotationstage												#Controler of the rotationstage
from seabreeze.spectrometers import list_devices, Spectrometer			


serialNumberTopas = "P18273"
comportStage = "COM3"

TOPAS = opa.Topas4OrpheusF(serialNumberTopas)
TOPAS.closeShutter()

SPECTROMETER = Spectrometer.from_first_available()
inttime = 100000
if int(inttime) < max(SPECTROMETER.integration_time_micros_limits):
	SPECTROMETER.integration_time_micros(int(inttime))

ROTATIONSTAGE = rotationstage.SMC100(1, 'COM3', silent=False)
ROTATIONSTAGE.reset_and_configure()
assert ROTATIONSTAGE.get_status()[0] == 0

root = tk.Tk()
gui = tkgui.GUI(root, TOPAS, SPECTROMETER, ROTATIONSTAGE)
gui.setup()


root.mainloop()