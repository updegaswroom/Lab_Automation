import Methods.savespectrafR as save
import Devices.OrphirPowermeter as PM
import numpy as np
import Methods.RemainingTime as crt
import time 
import win32gui
from threading import Thread
import Methods.CalculateTransmisionPower as TP
import Methods.calculatePeakIntensity as PI
import Methods.calculateBeamRadius as BR


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

def set_position(pos_deg, stage):
	stage.move_absolute_mm(pos_deg, waitStop=False)
	time.sleep(2)
	assert stage.get_status()[0] == 0
	#assert stage.get_status()[0] == 0 #not necessary if waitStop is true

def sweep_positions(positions, powers, ROTATIONSTAGE, TOPAS):
	monitorTime('Sweep start')
	TOPAS.openShutter()
	"""
	if iter < len(positions):
		set_position(positions[iter],ROTATIONSTAGE)
		powers[iter] = PM.getPower()
		iter = iter + 1
		sweep_positions(gui_instance,iter, positions, powers, ROTATIONSTAGE, TOPAS)
	"""
	for i in range(len(positions)):
		monitorTime('Sweep loop')
		set_position(positions[i],ROTATIONSTAGE)
		powers[i] = PM.getPower()
	TOPAS.closeShutter()
	monitorTime('Sweep stop')
	return powers

def measure(TOPAS, SPECTROMETER, ROTATIONSTAGE, sleeptime, positions, pos_index):
	monitorTime('I')
	set_position(float(positions[int(pos_index)]),ROTATIONSTAGE)
	monitorTime('am')
	TOPAS.openShutter()
	time.sleep(0.5)
	wavelengths, intensities = SPECTROMETER.spectrum(correct_dark_counts=False)
	time.sleep(sleeptime)
	monitorTime('still')
	measPower = PM.getPower()
	time.sleep(1)
	TOPAS.closeShutter()
	
	wavelengths = np.array(wavelengths)
	intensities = np.array(intensities)
	monitorTime('alive')
	return wavelengths, intensities, measPower
	
def monitorTime(Pos):
	global timeone, timezero
	timeone = time.time()
	print(str(Pos))
	print('time = %f' % (timeone - timezero))
	timezero = timeone

def startMeasurement(gui_instance, interaction, wavelength, numdatapoints,sampleID, opa, spectrom, rstage, *args):
	global timezero, timeone

	timezero = time.time()
	timeone = timezero
	monitorTime('start')	
	#global iteration, iteration2, wavelengths, intensities, accPower, accfR
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
	
	ROTATIONSTAGE = rstage
	
	positions = np.linspace(0,360,int(numdatapoints))
	powers = np.zeros(len(positions))
	time.sleep(10)
	win32gui.MessageBox(0, 'insert beamblocker in front of sample', '', 0)
	thread_status = ThreadWithReturnValue(target = sweep_positions, args = (positions, powers, ROTATIONSTAGE, TOPAS,))
	thread_status.start()
	powers = thread_status.join()
	win32gui.MessageBox(0, 'remove beamblocker in front of sample', '', 0)

	enum_pow = enumerate(powers)
	sorted_pow = sorted(enum_pow, key=lambda x: x[1])
	gui_instance.lines2.set_marker('x')
	gui_instance.lines2.set_linestyle('')
	gui_instance.ax2.set_xlim(min(powers),max(powers))
	gui_instance.parent.after(100, gui_instance.canvas_update)

	if gui_instance.HysteresisStatus:
		dummy_sorted_power_index = np.array(sorted_pow)
		sorted_power_index = np.concatenate((dummy_sorted_power_index[:,0],np.flip(dummy_sorted_power_index[:,0])), axis = 0)
		print(sorted_power_index)
	else: 
		dummy_sorted_power_index = np.array(sorted_pow)
		sorted_power_index = dummy_sorted_power_index[:,0]
		print(sorted_power_index)
	iteration = 0
	iteration2 = 0
	accPower = np.array([])
	accfR = np.array([])


	def disp_loop(gui_instance, timer, iteration2):
		TOPAS.setWavelength(gui_instance.config, int(gui_instance.disp_wavelengths[iteration2]))
		if (gui_instance.StartCond == True and iteration2 < len(gui_instance.disp_wavelengths)):
			iteration2 = iteration2 + 1
			iteration = 0
			inner_loop( gui_instance, Timer, iteration, accPower, accfR)
			disp_loop(gui_instance, timer, iteration2)
		elif gui_instance.StartCond == False:
			print("Measurement paused!")
			disp_loop(gui_instance, timer, iteration2)
		else:
			print("Dispersion measurement finished!")
	
	
	def inner_loop(gui_instance, timer, iteration, accPower, accfR):
		global darkintensities
		if (gui_instance.StartCond == True and iteration < len(sorted_power_index)):
			pos_index = sorted_power_index[iteration]
			hours, minutes = timer.getRemainingTimeHoursMins(iteration)
			gui_instance.RemainingTimeTextOut.delete('1.0', 'end')
			gui_instance.RemainingTimeTextOut.insert('end', str(hours) + " h " + str(minutes) +" min")

			if iteration == 0:
				darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False)
				time.sleep(1)
				darkwavelengths = np.array(darkwavelengths)
				darkintensities = np.array(darkintensities)
				save.savespectrafR(ID = sampleID, Inttime = gui_instance.intt, OPALambda = wavelength,Power = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
			
			thread_measure = ThreadWithReturnValue(target = measure, args = (TOPAS, SPECTROMETER, ROTATIONSTAGE, sleeptime, positions, pos_index,))
			thread_measure.start()
			
			wavelengths, intensities, measPower = thread_measure.join()
			inties = intensities-darkintensities
			SHGsearch = inties[(wavelengths > (wavelength/2 - 20)) & (wavelengths < (wavelength/2 + 20))]
			THGsearch = inties[(wavelengths > (wavelength/3 - 20)) & (wavelengths < (wavelength/3 + 20))]
			
			SHG = np.max(SHGsearch)
			THG = np.max(THGsearch)
			calcfR = np.power(SHG,3)/np.power(THG,2)
			accfR = np.append(accfR,np.absolute(calcfR)+1)
			accPower = np.append(accPower,measPower)
			save.savespectrafR(ID = sampleID, Inttime = gui_instance.intt, OPALambda = wavelength,Power = measPower, Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
			
			Lambda = wavelength
			BeamRadiusLense = 1e-3
			FocalDistance = 150e-3
			M = 1.2
			z = 5e-3
			MeasPower = measPower
			BeamRadius = BR.BeamRadius(Lambda, FocalDistance, BeamRadiusLense, M, z)
			PulsePower = TP.CalcSamplePower(Lambda, MeasPower, x, y)
			RepRate = 50e3
			PulseDuration = 100e-15
			PeakInt = PI.PeakInt(BeamRadius, PulseDuration, PulsePower, RepRate)
			accPeakInt = np.append(accPeakInt, PeakInt)

			gui_instance.lines1.set_xdata(wavelengths)
			gui_instance.lines1.set_ydata(inties)
			#gui_instance.lines2.set_xdata(accPower)
			gui_instance.lines2.set_xdata(accPeakInt)
			gui_instance.lines2.set_ydata(accfR)
			gui_instance.ax1.set_ylim(-1e3,max(inties)+1e3)
			gui_instance.ax2.set_ylim(min(accfR)*0.001,max(accfR)*10)
			#gui_instance.ax2.set_xlim(min(accPower)-0.01, max(accPower)+0.01)
			gui_instance.ax2.set_xlim(0.9*min(accPeakInt), 1.1*max(accPeakInt))
			#gui_instance.parent.after(100, gui_instance.canvas_update) # is this still necessary?
			iteration = iteration + 1
			gui_instance.parent.update_idletasks()
			inner_loop(gui_instance, Timer, iteration, accPower, accfR)
		elif gui_instance.StartCond == False:
			print("Measurement paused!")
			inner_loop(gui_instance, Timer, iteration, accPower, accfR)
		else:
			win32gui.MessageBox(0, "Measurement finished!", '', 0)

	

	if gui_instance.DispersionStatus:
		if interaction == "IDL" or "CMP-IDL":
			DispWavelengths = np.linspace(1200,1800,13)
			Timer.setStartTime(len(sorted_power_index)*len(DispWavelengths))
			disp_loop(gui_instance, Timer, iteration2)
	else:
		Timer.setStartTime(len(sorted_power_index))
		inner_loop(gui_instance, Timer, iteration, accPower, accfR)