import Methods.savespectraSFG as save
import Devices.OrphirPowermeter as PM
import numpy as np
import Methods.RemainingTime as crt
import time 
from threading import Thread
import random
import win32gui

timezero = time.time()
timeone = timezero

class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def set_position(pos_mm, stage):
	stage.move_abs(pos_mm,checkmovement = True)
	#assert stage.get_status()[0] == 0 #not necessary if waitStop is true

def set_position_rel(rel_mm, stage):
	stage.move_rel(rel_mm, checkmovement = True)

def measure(TOPAS, SPECTROMETER, DELAYSTAGE, sleeptime, distribution, iteration):
	monitorTime('Measure start')
	set_position(distribution[iteration][1], DELAYSTAGE) # +random.randint(-2,2) for testing purposes

	TOPAS.openShutter()
	time.sleep(0.5)
	wavelengths, intensities = SPECTROMETER.spectrum(correct_dark_counts=False)
	time.sleep(sleeptime)
	TOPAS.closeShutter()
	
	wavelengths = np.array(wavelengths)
	intensities = np.array(intensities)
	monitorTime('Measure end')
	return wavelengths, intensities
	
def monitorTime(Pos):
	timeone = time.time()
	print(str(Pos))
	print('time = %f' % (timezero - timeone))
	timezero = timeone

def startMeasurement(gui_instance, interaction, wavelength, numdatapoints, sampleID, opa, spectrom, delayl, *args):
	monitorTime('start')	
	c = 299792458
	DT = 2*1e-12
	DX = c*DT/2	
	Timer = crt.timer()

	TOPAS = opa
	TOPAS.setWavelength(interaction, int(wavelength))
	
	SPECTROMETER = spectrom
	if int(gui_instance.intt) < max(SPECTROMETER.integration_time_micros_limits):
		SPECTROMETER.integration_time_micros(int(gui_instance.intt))

	if gui_instance.intt <= 1e6/2:
		sleeptime = 0.5
	else: 
		sleeptime = gui_instance.intt/1e6
	
	DELAYSTAGE = delayl

	zero = float(DELAYSTAGE.get_position())								#get current zero position, just to make sure, move stage in absolute units relative to zero, as purely relative units require additional code for correction for the previous step
	u = np.arange(0,1,1/numdatapoints)	
	alpha = DX/np.tan(np.pi*(max(u)-1/2))								#rough estimation of the alpha value of cauchy distribution --> has to be optimized manually
	#exp = -1/lam*np.log(1-u)											#use requires additional copy and inversion of datapoints as the pdf is positive definite on x
	cauchy = np.tan(np.pi*(u-1/2))*alpha*250 + zero						#map uniform datapoints to cauchy distributed datapoints
	arr = cauchy[(cauchy >= -DX+zero) & (cauchy <= DX+zero)]			#exclude all datapoints out of range of interest
	arr_enum = list(enumerate(arr))

	"""
	check if all datapoints lie within the range of the delayline
	"""
	
	distribution = arr_enum
	random.shuffle(distribution)										#randomize the order of measurement points
	
	def inner_loop(gui_instance, timer, iteration):
		if (gui_instance.StartCond == True and iteration < len(distribution)):
					
			hours, minutes = timer.getRemainingTimeHoursMins(iteration)
			gui_instance.RemainingTimeTextOut.delete('1.0', 'end')
			gui_instance.RemainingTimeTextOut.insert('end', str(hours) + " h " + str(minutes) +" min")

			if iteration == 0:
				darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False)
				time.sleep(1)
				darkwavelengths = np.array(darkwavelengths)
				darkintensities = np.array(darkintensities)
				save.savespectraSFG(ID = sampleID, Inttime = gui_instance.intt, OPALambda = wavelength, Position = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
			
			thread_measure = ThreadWithReturnValue(target = measure, args = (TOPAS, SPECTROMETER, DELAYSTAGE, sleeptime, distribution, iteration))
			thread_measure.start()
			wavelengths, intensities = thread_measure.join()

			monitorTime('Graphics start')
			save.savespectraSFG(ID = sampleID, Inttime = gui_instance.intt, OPALambda = wavelength, Position = distribution[:][1], Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
		
			gui_instance.Z[:,distribution[iteration][0]] = intensities - darkintensities
			gui_instance.lines.set_xdata(wavelengths)
			gui_instance.lines.set_ydata(intensities - darkintensities)
			gui_instance.ax1.set_ylim(-1e3,max(intensities - darkintensities)+1e3)

			gui_instance.lines2.set_data(gui_instance.Z)
			gui_instance.lines2.set_clim(vmin=0,vmax=np.amax(gui_instance.Z))

			gui_instance.parent.after(100, gui_instance.canvas_update)
			iteration = iteration + 1
			monitorTime('Graphics stop')
			gui_instance.parent.update_idletasks()
			inner_loop(gui_instance, Timer, iteration)
		elif gui_instance.StartCond == False:
			print("Measurement paused!")
			inner_loop(gui_instance, Timer, iteration)
		else:
			win32gui.MessageBox(0, "Measurement finished!", '', 0)
			#print("Measurement finished!")
			#print(accfR)
	

	Timer.setStartTime(len(distribution[:][1]))
	inner_loop(gui_instance, Timer, iteration = 0)