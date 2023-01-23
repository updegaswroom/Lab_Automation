import Devices.TOPAS4OrpheusF_NET_SDK as OPA
import Devices.OrphirPowermeter as PM
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

directory = os.getcwd()
filename = "PowerVsWavelengthReflection.txt"
filepath = os.path.join(directory,filename)

serialNumberTopas = "P18273"
comportStage = "COM3"
"""self.options = [
			"SIG LONG",
			"SIG",
			"IDL LONG",
			"IDL",
			"CMP-SIG",
			"CMP-IDL"]"""
TOPAS = OPA.Topas4OrpheusF(serialNumberTopas)
TOPAS.closeShutter()


NumberOfDatapoints = 50
interaction = "CMP-IDL"
Wavelengths = np.linspace(1130, 2000, NumberOfDatapoints)
Powers = np.zeros(len(Wavelengths))

for i in range(len(Wavelengths)):
    TOPAS.setWavelength(interaction, int(Wavelengths[i]))
    TOPAS.openShutter()
    sleep(1)
    Powers[i] = PM.getPower()
    sleep(1)
    TOPAS.closeShutter()
    sleep(1)

plt.plot(Wavelengths, Powers, 'x')
plt.show()


dateTimeObj = datetime.now()

with open(filepath, 'w') as f:
			timestamp = dateTimeObj.strftime("%Y %m %d (%H-%M)")
			f.write(f"Date {timestamp} ) \n")
			f.write(f"Interaction: {interaction} \n")
			for index in range(len(Wavelengths)):
				f.write("%d" % Wavelengths[index])
				f.write("\t")
				f.write("%5f" % Powers[index])
				f.write("\n")
