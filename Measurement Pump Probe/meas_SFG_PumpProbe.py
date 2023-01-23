import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import numpy as np
import time 
import random
import tkinter as tk
import Methods.savespectraSFG as save
import Devices.MM4006 as delaystage												#Controler of the delaystage
import Devices.TOPAS4OrpheusF_NET_SDK as opa											#OPA	
import seabreeze														#spectrometer
from seabreeze.spectrometers import list_devices, Spectrometer			
import Devices.OrphirPowermeter as POWERMETER									#Powermeter

###################### set measurement parameters ######################
DT = 2*1e-12															#The mesurement points will be acquired in the time range of +/i DT
numberofdatapoints = 1000												#define the number of datapoints to be acquired (actual number will be lower as array is truncated after mapping procedure)
sampleID = "LNT_25_75_2"

""" Full sample ID List containing Nb/Ta content and number of batch it was delivered in 
"LNT_000_100_02"
"LNT_025_075_02"
"LNT_050_050_02"
"LNT_075_025_02"
"LNT_100_000_01"
"""
############################# GUI stuff ###############################

cond = False 
data = np.array([])
root = tk.Tk()
root.title('SFG Pump Probe Measurement')
root.configure(background = 'light blue')
root.geometry('1000x500')
distribution = np.array([])
##### create plot object on GUI #####

fig = Figure()
ax = fig.add_subplot(1,2,1)
ax.set_title('Live Spectra')
ax.set_xlabel('Wavelength')
ax.set_ylabel('Counts')
ax.set_xlim(266,1057)
ax.set_ylim(-0.5,10000)
lines = ax.plot([],[])[0]												#gives an array in whcih we can set x and y data later on to have astatic axes window

ax2 = fig.add_subplot(1,2,2)
x = np.linspace(-10,10,10) #distribution
y = np.linspace(266, 1057, 10)#wavelengths
z = np.array([random.randint(0,1) for j in x for i in y])
Z = z.reshape(len(y), len(x))

lines2 = ax2.imshow(Z, interpolation='nearest', 
                            #origin='lower', 
                           extent=[min(x),max(x),min(y),max(y)],
                           aspect='auto', # get rid of this to have equal aspect 
                           cmap='jet')
cbar = fig.colorbar(lines2)



canvas = FigureCanvasTkAgg(fig, master = root)
canvas.get_tk_widget().place(x=10,y=10, width = 800, height = 400)
canvas.draw()

##### create buttons #####


root.update()
start = tk.Button(root, text = 'Start measurement', font = ('calibri',12), bg='green', command = lambda: startMeasurement())
start.place(x = 850, y = 400)

root.update()
stop = tk.Button(root, text = 'Abort measurement', font = ('calibri',12), bg='red')
stop.place(x = 850, y = 450)

root.update()
RemainingTimeText = tk.Text(height=1,width=15, bg = 'light blue')
RemainingTimeText.place(x = 850, y = 25)
RemainingTimeText.insert('end', 'Remaining time')
RemainingTimeText.config(state='disabled')
RemainingTimeTextOut= tk.Text(height=1,width=15)
RemainingTimeTextOut.place(x = 850, y = 50)
RemainingTimeTextOut.insert('end', 'NONE')

def plot_data():
	global cond
	#print("Hello") 
	if (cond == True):
		#data = np.append(data,random.randint(0,100))
		#print(Z[:,iteration-1])
		#lines2.set_data(Z)
		canvas.draw() 
	root.after(100,plot_data)

def plot_start():
	global cond
	cond = True
def plot_stop():
	global cond
	cond = False
def read_input_field():
	current_input = NumDataPoints.get()
	print(current_input)
#######################################################################
#implement a testing device in every individual module to test them individually during the troubleshooting stage
#finalize MM4006
"""
Available interactions:
SIG LONG 630 - 1020 nm
SIG 640 - 940 nm
IDL LONG 1032 - 2762 nm
IDL 1129 - 2585 nm
CMP-SIG 640 - 940 nm
CMP-IDL 1129 - 2585 nm
"""
########################### initialization #############################
def startMeasurement():
	global distribution, iteration, cond, Z, wavelengths, intensities, start_time
	serialNumberTopas = "P18273"												#serial number of OPA
	comportStage = "COM3"													#comport of Delaystage
	interaction = "IDL"
	wavelength = 1200 													#(1400+1030 --> 593 nm) (1200+1030 --> 554 nm) 
																		#--> in these cases a clear spectral separation of SHG and SFG signals is given
	inttime = 1*1e6 														#set integration time in microseconds
	#make automatic inttime adjustment
	c = 299792458
	DX = c*DT/2																#division by a factor of 2 is required, as the delaystage movement by x equals the double of lightpath DX = 2x
																		

	TOPAS = opa.Topas4OrpheusF(serialNumberTopas)							#connect to OrpheusF and initialize
	TOPAS.closeShutter()
	TOPAS.setWavelength(interaction, wavelength)

	CONTROLER = delaystage.NewportMM4006(comportStage)								#Connect to Controler
	DELAYSTAGE = delaystage.Axis(CONTROLER, 3)													#Connect to Delaystage, located at axis 4 (i.e. controlunit 4)
	DELAYSTAGE.unit()															#get information of the displacement unit
	DELAYSTAGE.motor_on()														#turn on motor so the delaystage can be moved
	time.sleep(2)
	#print(DELAYSTAGE.id())														#check for correct ID(add this)
#(assure that ID is correct)
	zero = float(DELAYSTAGE.get_position())												#get current zero position, just to make sure, move stage in absolute units relative to zero, as purely relative units require additional code for correction for the previous step
	#print(zero)
#########

	u = np.arange(0,1,1/numberofdatapoints)
	alpha = DX/np.tan(np.pi*(max(u)-1/2))									#rough estimation of the alpha value of cauchy distribution --> has to be optimized manually
	#exp = -1/lam*np.log(1-u)												#use requires additional copy and inversion of datapoints as the pdf is positive definite on x
	cauchy = np.tan(np.pi*(u-1/2))*alpha*250 + zero							#map unfigorm datapoints to cauchy distributed datapoints
	arr = cauchy[ (cauchy >= -DX+zero) & (cauchy <= DX+zero) ]			#exclude all datapoints out of range of interest
	arr_enum = list(enumerate(arr))
	"""
	check if all datapoints lie within the range of the delayline
	"""
	distribution = arr_enum
	random.shuffle(distribution)

#########
	SPECTROMETER = Spectrometer.from_first_available()						#find and connect to available spectrometer
	if inttime < max(SPECTROMETER.integration_time_micros_limits): 					#check if the set integration time is in a valid range
		SPECTROMETER.integration_time_micros(inttime)



########################## data acquisition ############################
	start_time = time.time()
	cond = True
	iteration = 0
	dislen = len(arr)
	x = np.linspace(min(arr),max(arr),dislen) #distribution
	y = np.linspace(266, 1057, 1044)#wavelengths
	z = np.array([random.randint(0,1) for j in x for i in y])
	Z = z.reshape(len(y), len(x))
	
	
	TOPAS.closeShutter()
	time.sleep(0.5)
	darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False) 
	time.sleep(2*inttime/1e6)
	save.savespectraSFG(ID = sampleID, Inttime = inttime, OPALambda = wavelength,Position = zero, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True, silent = False)
	def inner_loop():
		global distribution, iteration, start_time, Z
		
		if (cond == True and iteration < len(distribution)):
		
			elapsed_time = time.time() - start_time
			average_time = elapsed_time/(iteration+1) 
			remaining_time = (dislen - iteration)*average_time
			minutes = int((remaining_time // 60)%60)
			hours = int(remaining_time // 3600)
			RemainingTimeTextOut.delete('1.0', 'end')
			RemainingTimeTextOut.insert('end', str(hours) + " h " + str(minutes) +" min")

			distribution[iteration][1]
			DELAYSTAGE.move_abs(distribution[iteration][1]+random.randint(-2,2))   #+random.randint(-1,1) for testing purposes
			time.sleep(2)
			#DELAYSTAGE.movingfinished()
			#average multiple times?
			TOPAS.openShutter()
			wavelengths, intensities = SPECTROMETER.spectrum(correct_dark_counts=False) 
			time.sleep(4*inttime/1e6)
			TOPAS.closeShutter()
			save.savespectraSFG(ID = sampleID, Inttime = inttime, OPALambda = wavelength,Position = distribution[iteration][1], Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
			time.sleep(2*inttime/1e6)

			Z[:,distribution[iteration][0]] = intensities - darkintensities
			lines.set_xdata(wavelengths)
			lines.set_ydata(intensities - darkintensities)
			lines2.set_data(Z)
			lines2.set_clim(vmin=0,vmax=np.amax(Z))
			canvas.draw()
			iteration = iteration + 1 
			root.after(100,inner_loop)
		else:
			print("Measurement finished!")
	inner_loop()

root.mainloop()

'''old code of for loop
for pos in distribution:
		iteration = iteration + 1 											#active time monitoring in order to estimate the ramaining measurement time
		elapsed_time = time.time() - start_time
		average_time = elapsed_time/iteration 
		remaining_time = (dislen - iteration)*average_time
		print(str(round(remaining_time,1)) + " seconds remaining")
	
		DELAYSTAGE.move_abs(pos)   #+random.randint(-1,1) for testing purposes
		time.sleep(2)
		#DELAYSTAGE.movingfinished()
		#average multiple times?
		TOPAS.openShutter()
		wavelengths, intensities = SPECTROMETER.spectrum(correct_dark_counts=False) 
		time.sleep(2*inttime/1e6)
		TOPAS.closeShutter()
		save.savespectraSFG(ID = sampleID, Inttime = inttime, OPALambda = wavelength,Position = pos, Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
		time.sleep(2*inttime/1e6)
		#plot_data(wavelengths,intensities)
		Z[:,iteration-1] = intensities - darkintensities
		#root.after(100,plot_data)
	print("Measurement finished!")
'''
