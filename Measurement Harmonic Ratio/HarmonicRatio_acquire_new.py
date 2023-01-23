import Methods.savespectrafR as save
import Methods.calculateBeamRadius as BR
import Methods.calculateTransmisionPower as TP
import Methods.calculatePeakIntensity as PI
import Devices.OrphirPowermeter as PM
import numpy as np
import Methods.RemainingTime as crt
import time 
import win32gui
from threading import Thread


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

def start_measurement(gui_instance, RSTAGE, TOPAS, SPECTROM):
	Timer = crt.timer()
	RSTAGE.home()
	TOPAS.closeShutter()
	if int(gui_instance.intt) < max(SPECTROM.integration_time_micros_limits):
		SPECTROM.integration_time_micros(int(gui_instance.intt))

	if gui_instance.intt <= 1e6/2:
		sleeptime = 0.5
	else: 
		sleeptime = gui_instance.intt/1e6
	home_offset = set_home_software(RSTAGE)
	positions = np.linspace(0+home_offset,-330+home_offset,int(gui_instance.numdp))
	"""
	thread_status = ThreadWithReturnValue(target = sweep_positions, args = (gui_instance,TOPAS, RSTAGE, positions, False, ))
	thread_status.start()
	powers = thread_status.join()
	sorted_pow = sorted(enum_pow, key=lambda x: x[1])"""
	enum_pos = enumerate(positions)
	sorted_pos = np.array(sorted(enum_pos, key=lambda x: x[0]))
	gui_redraw_init(gui_instance)
	if gui_instance.HysteresisStatus:
		dummy_sorted_power_index = sorted_pos
		sorted_power_index = np.concatenate((dummy_sorted_power_index[:,0],np.flip(dummy_sorted_power_index[:,0])), axis = 0)
	else: 
		dummy_sorted_power_index = sorted_pos
		sorted_power_index = dummy_sorted_power_index[:,0]

	if gui_instance.DispersionStatus:
		if gui_instance.config == "IDL" or "CMP-IDL":
			Timer.setStartTime(len(sorted_power_index)*len(gui_instance.disp_wavelengths))
			measurement_dispersion(gui_instance, RSTAGE, TOPAS, SPECTROM, gui_instance.disp_wavelengths, positions, sorted_power_index, Timer, sleeptime)
		else:
			print('config not supported')
	else:
		Timer.setStartTime(len(sorted_power_index))
		measurement(gui_instance, RSTAGE, TOPAS, SPECTROM, gui_instance.wavel, positions, sorted_power_index, Timer, 1, sleeptime)
	print("measurement done")
	gui_instance.resetAfterMeasurement()	
	
def set_position(RSTAGE, pos_deg, checkDone = False):
	pos_round = np.round(pos_deg,2)
	RSTAGE.move_absolute_mm(pos_round, waitStop=False)
	time.sleep(.5)
	if checkDone:
		try:
			assert RSTAGE.get_status()[0] == 0
		except AssertionError as e:
			print(e)
			RSTAGE.reset_and_configure() # maybe not necessary to get of of not referenced mode
			RSTAGE.home()
			set_position(RSTAGE, pos_round, checkDone = True)

def set_home_software(RSTAGE):
	"""RSTAGE.home()
	pos_home = RSTAGE.get_position_mm()
	RSTAGE.move_absolute_mm()
	pos_software_home = RSTAGE.get_position_mm()
	home_offset = pos_software_home - pos_home"""
	home_offset = -20
	return home_offset

def sweep_positions(gui_instance,TOPAS, RSTAGE, positions, wavelength, shutter = False):
	TOPAS.setWavelength(gui_instance.config, int(gui_instance.wavel))
	if shutter:
		win32gui.MessageBox(0, 'insert beamblocker in front of sample', '', 0)
	TOPAS.openShutter()
	
	powers = np.zeros(len(positions))
	for i in range(len(positions)):
		set_position(RSTAGE, positions[i], checkDone = True)
		powers[i] = PM.getPower()
	
	TOPAS.closeShutter()
	if shutter:
		win32gui.MessageBox(0, 'remove beamblocker in front of sample', '', 0)

	return powers

def measurement_dispersion(gui_instance, RSTAGE, TOPAS, SPECTROM, wavelengths, positions, sorted_power_index, Timer, sleeptime):

	for j in range(wavelengths):
		darkwavelengths, darkintensities = SPECTROM.spectrum(correct_dark_counts=False)
		save.savespectrafR(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = wavelengths[j],Power = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
		measurement(gui_instance, RSTAGE, TOPAS, SPECTROM, wavelengths[j], positions, sorted_power_index, Timer, j+1, sleeptime)

def measurement(gui_instance, RSTAGE, TOPAS, SPECTROM, wavelength, positions, sorted_power_index, Timer, IterDisp, sleeptime):
	TOPAS.closeShutter()
	TOPAS.setWavelength(gui_instance.config, int(wavelength))
	darkwavelengths, darkintensities = SPECTROM.spectrum(correct_dark_counts=False)
	save.savespectrafR(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = wavelength,Power = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
	accfR = np.array([])
	accInt = np.array([])
	for i in range(len(sorted_power_index)):
		currentIteration = i*IterDisp
		pos_index = sorted_power_index[i]
		set_position(RSTAGE, float(positions[int(pos_index)]), checkDone = True)
		TOPAS.openShutter()
		time.sleep(sleeptime)
		wavelengths, intensities = SPECTROM.spectrum(correct_dark_counts=False)
		time.sleep(sleeptime)
		measPower = PM.getPower_auto()
		time.sleep(1)
		save.savespectrafR(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = wavelength,Power = measPower, Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
		TOPAS.closeShutter()
		fR, Int = get_harmonicRatio(wavelengths, intensities-darkintensities, wavelength, measPower)
		accInt = np.append(accInt, Int)
		accfR = np.append(accfR, fR)
		gui_redraw(gui_instance, wavelengths, intensities-darkintensities, accInt, accfR)
		gui_update_timer(gui_instance, Timer, currentIteration)

def gui_redraw(gui_instance, X1data, Y1data, X2data, Y2data):
	gui_instance.lines1.set_xdata(X1data)
	gui_instance.lines1.set_ydata(Y1data)
	gui_instance.ax1.set_ylim(-1e3,max(Y1data)+1e3)

	gui_instance.lines2.set_xdata(X2data)
	gui_instance.lines2.set_ydata(Y2data)
	gui_instance.ax2.set_xlim(min(X2data)-0.1*max(X2data), 1.1*max(X2data))
	gui_instance.ax2.set_ylim(0.9*min(Y2data),1.1*max(Y2data))

	gui_instance.parent.after(100, gui_instance.canvas_update)
	gui_instance.parent.update_idletasks()

def gui_redraw_init(gui_instance):
	gui_instance.lines2.set_marker('x')
	gui_instance.lines2.set_linestyle('')
	#gui_instance.ax2.set_xlim(min(powers),max(powers))
	gui_instance.parent.after(100, gui_instance.canvas_update)

def gui_update_timer(gui_instance, Timer, currIteration):
	hours, minutes = Timer.getRemainingTimeHoursMins(currIteration)
	gui_instance.RemainingTimeTextOut.delete('1.0', 'end')
	gui_instance.RemainingTimeTextOut.insert('end', str(hours) + " h " + str(minutes) +" min")

def get_harmonicRatio(wavelengths, inties, wavelength, measPower):
	SHGsearch = inties[(wavelengths > (wavelength/2 - 20)) & (wavelengths < (wavelength/2 + 20))]
	THGsearch = inties[(wavelengths > (wavelength/3 - 20)) & (wavelengths < (wavelength/3 + 20))]	
	SHG = np.max(SHGsearch)
	THG = np.max(THGsearch)
	calcfR = np.power(SHG,3)/np.power(THG,2)
	peakInt = get_PeakIntensity(wavelength, measPower)
	fR = np.absolute(calcfR)

	return fR, peakInt

def get_PeakIntensity(Lambda, MeasPower):
	Lambda_meters = Lambda*1e-9
	RepRate = 50e3 # repetition rate
	PulseDuration = 100e-15 # pulse duration
	FocalDistance = 150e-3# focal distance of lense
	BeamRadiusLense = 1e-3# Beam Radius of light at the position of the lense
	M = 1.2 # M value of the Laser
	z = 10e-3 # distance: focal point -- sample
	BeamRadius = BR.BeamRadius(Lambda_meters, FocalDistance, BeamRadiusLense, M, z) # calculates the beam radius at the sample position
	PulsePower = TP.CalcSamplePower(Lambda, MeasPower) # calculates the Power of the transmitted beam
	PeakInt = PI.PeakInt(BeamRadius, PulseDuration, PulsePower, RepRate) # calculates the corresponding pulses peak intensity
	return PeakInt 

def monitorTime(Message):
	global timeone, timezero

	timeone = time.time()
	if timezero == None:
		timezero = timeone

	print(str(Message))
	print('time = %f' % (timeone - timezero))
	timezero = timeone

def set_Inttime_SP_auto(SPECTROM, TOPAS):
	return 1
def set_Inttime_SP(SPECTROM, TOPAS, inttime):
	return 1

# update savefile so repeated measurements with same sample show a different indication/iteration

if __name__ == '__main__':
	peakInt = get_PeakIntensity(1400, 0.05)

"""
TODO:
automatische range anpassung
dereferenzierung von SMC100
live anzeige des spektrometers zur kalibration der intzeit
wavelength display
input fields for PeakInt calculation
stage home reset
speicher version safe
buffer of PM has to be flushed after every measurement/ range change! first value is always "old"
allow for multiple measurments to follow so reuse gui after meas done
nach wie vor: erste messung gibt falsche leistung an evtl zu nah an range grenze
wellenlaengen korrektur im pm
pm range issue first buffer value not flushed... ommit first measurement
"""