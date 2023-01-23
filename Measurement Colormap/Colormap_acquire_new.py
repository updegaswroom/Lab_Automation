import Methods.savespectrafR as save
import Methods.calculateBeamRadius as BR
import Methods.calculateTransmisionPower as TP
import Methods.calculatePeakIntensity as PI
import Devices.OrphirPowermeter as PM
import numpy as np
import random
import Methods.RemainingTime as crt
import time 
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

def start_measurement(gui_instance, TOPAS, SPECTROM, RSTAGE):
	Timer = crt.timer()
	RSTAGE.home()
	TOPAS.closeShutter()
	inttime = gui_instance.intt
	sleeptime = setup_spectrometer(SPECTROM, inttime)
	position = 20
	set_position(RSTAGE, position)
	Timer.setStartTime(len(gui_instance.wavelengths))

	darkwavelengths, darkintensities = measurement(gui_instance, TOPAS, SPECTROM, Timer, sleeptime, inttime, 0, dark = True)
	gui_redraw_init(gui_instance,darkwavelengths)
	for iter in range(len(gui_instance.wavelengths)):
		sleeptime = setup_spectrometer(SPECTROM, inttime)
		wavelengths, intensities = measurement(gui_instance, TOPAS, SPECTROM, Timer, sleeptime, inttime, iter, dark = False)	
		gui_redraw(gui_instance, darkintensities, intensities, wavelengths, iter)
		gui_update_timer(gui_instance, Timer, iter)
		if not gui_instance.StartCond:
			print('Measurement Aborted')
			break
		
	TOPAS.closeShutter()		
	print("measurement done")
	gui_instance.resetAfterMeasurement()	

def measurement(gui_instance, TOPAS, SPECTROM, Timer, sleeptime, inttime, iter, dark = False):
		if dark:
			TOPAS.closeShutter()
			time.sleep(0.5)
			darkwavelengths, darkintensities = SPECTROM.spectrum(correct_dark_counts=False)
			time.sleep(sleeptime)
			save.savespectrafR(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = 0,Power = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
			return darkwavelengths, darkintensities
		else:
			print("Wavelength:" + str(gui_instance.wavelengths[iter]))
			TOPAS.setWavelength(gui_instance.config, int(gui_instance.wavelengths[iter]))
			TOPAS.openShutter()
			time.sleep(sleeptime)
			wavelengths, intensities = SPECTROM.spectrum(correct_dark_counts=False)
			time.sleep(sleeptime)
			measPower = PM.getPower_auto()

			if gui_instance.autoint:
				if max(intensities) < 5e5 and inttime <= gui_instance.max_inttime/2:
					print(inttime)
					inttime = inttime*2
					setup_spectrometer(SPECTROM, inttime)
					measurement(gui_instance, TOPAS, SPECTROM, Timer, sleeptime, inttime, iter, dark = False)
			else:
				save.savespectrafR(ID = gui_instance.sampleID, Inttime = inttime, OPALambda = gui_instance.wavelengths[iter],Power = measPower, Wavelengths = wavelengths, Intensities = intensities, DarkSpectra = False)
				return wavelengths, intensities	

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

def setup_spectrometer(SPECTROM, inttime):
	if int(inttime) < max(SPECTROM.integration_time_micros_limits):
		SPECTROM.integration_time_micros(int(inttime))

	if inttime <= 1e6/2:
		sleeptime = 0.5
	else: 
		sleeptime = inttime/1e6
	return sleeptime

def gui_redraw(gui_instance, darkintensities, intensities, wavelengths, iteration):

	gui_instance.lines1.set_xdata(wavelengths)
	gui_instance.lines1.set_ydata(intensities - darkintensities)
	gui_instance.ax1.set_ylim(-1e3,max(intensities - darkintensities)+1e3)
	dummyx = range(len(gui_instance.wavelengths))
	gui_instance.Z[:,dummyx[iteration]] = np.flip(intensities - darkintensities)
	gui_instance.lines2.set_data(gui_instance.Z)
	gui_instance.lines2.set_clim(vmin=0,vmax=np.amax(gui_instance.Z))

	gui_instance.parent.after(100, gui_instance.canvas_update)
	gui_instance.parent.update_idletasks()

def gui_redraw_init(gui_instance,wavelengths):
	x = gui_instance.wavelengths
	y = wavelengths
	z = np.array([random.randint(0,1) for j in x for i in y])
	gui_instance.Z = z.reshape(len(y), len(x))   
	gui_instance.lines2.set_data(gui_instance.Z)
	gui_instance.lines2.set_clim(vmin=0,vmax=np.amax(gui_instance.Z))

	gui_instance.parent.after(100, gui_instance.canvas_update)

def gui_update_timer(gui_instance, Timer, currIteration):
	hours, minutes = Timer.getRemainingTimeHoursMins(currIteration)
	gui_instance.RemainingTimeTextOut.delete('1.0', 'end')
	gui_instance.RemainingTimeTextOut.insert('end', str(hours) + " h " + str(minutes) +" min")

# update savefile so repeated measurements with same sample show a different indication/iteration

if __name__ == '__main__':
	print('Test')