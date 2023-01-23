import Methods.savespectraSFG as save
import Devices.OrphirPowermeter as PM
import numpy as np
import Methods.RemainingTime as crt
import time 
from threading import Thread
import random
import win32gui

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

def gui_redraw(gui_instance, distribution, darkintensities, intensities, wavelengths, iteration):

	gui_instance.lines.set_xdata(wavelengths)
	gui_instance.lines.set_ydata(intensities - darkintensities)
	gui_instance.ax1.set_ylim(-1e3,max(intensities - darkintensities)+1e3)

	gui_instance.Z[:,distribution[iteration][0]] = intensities - darkintensities
	gui_instance.lines2.set_data(gui_instance.Z)
	gui_instance.lines2.set_clim(vmin=0,vmax=np.amax(gui_instance.Z))

	gui_instance.parent.after(100, gui_instance.canvas_update)
	gui_instance.parent.update_idletasks()

def gui_redraw_init(gui_instance, distribution, wavelengths):
	x = distribution
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

def startMeasurement(gui_instance, DELAYLINE, TOPAS, SPECTROM):      
    Timer = crt.timer()
    #gui_redraw_init(gui_instance)
    c = 299792458
    DT = 2*1e-12
    DX = c*DT/2	

    TOPAS.closeShutter()
    TOPAS.setWavelength(gui_instance.config, int(gui_instance.wavel))
	

    if int(gui_instance.intt) < max(SPECTROM.integration_time_micros_limits):
        SPECTROM.integration_time_micros(int(gui_instance.intt))

    if gui_instance.intt <= 1e6/2:
        sleeptime = 0.5
    else: 
        sleeptime = gui_instance.intt/1e6
	
    zero = float(DELAYLINE.get_position())								#get current zero position, just to make sure, move stage in absolute units relative to zero, as purely relative units require additional code for correction for the previous step
    u = np.arange(0,1,1/gui_instance.numdp)	
    alpha = DX/np.tan(np.pi*(max(u)-1/2))								#rough estimation of the alpha value of cauchy distribution --> has to be optimized manually
    #exp = -1/lam*np.log(1-u)											#use requires additional copy and inversion of datapoints as the pdf is positive definite on x
    cauchy = np.tan(np.pi*(u-1/2))*alpha*250 + zero						#map uniform datapoints to cauchy distributed datapoints
    arr = cauchy[(cauchy >= -DX+zero) & (cauchy <= DX+zero)]			#exclude all datapoints out of range of interest
    arr_enum = list(enumerate(arr))
    distribution = arr_enum
    random.shuffle(distribution)										#randomize the order of measurement points
    Timer.setStartTime(len(distribution[:][1]))

    for iteration in range(len(arr)):
        pos = distribution[iteration][1]
        if iteration == 0:
            darkwavelengths, darkintensities = measure(gui_instance, TOPAS, SPECTROM, DELAYLINE, sleeptime, pos, iteration, dark = True)
            gui_redraw_init(gui_instance, arr, wavelengths)
        wavelengths, intensities = measure(gui_instance, TOPAS, SPECTROM, DELAYLINE, sleeptime, distribution, iteration, dark = False)
		
        gui_redraw(gui_instance, gui_instance, distribution, darkintensities, intensities, wavelengths, iteration)
        gui_update_timer(gui_instance, Timer, iteration)


    print("measurement done")
    gui_instance.resetAfterMeasurement()

def measure(gui_instance, TOPAS, SPECTROMETER, DELAYSTAGE, sleeptime, pos, dark = False):

    if dark == True:
        darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False)
        darkwavelengths = np.array(darkwavelengths)
        darkintensities = np.array(darkintensities)
        time.sleep(sleeptime)
        save.savespectraSFG(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = gui_instance.wavel, Position = 0, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = True)
        return darkwavelengths, darkintensities
    else:

        set_position(pos, DELAYSTAGE) # +random.randint(-2,2) for testing purposes
        TOPAS.openShutter()
        time.sleep(sleeptime)
        wavelengths, intensities = SPECTROMETER.spectrum(correct_dark_counts=False)
        time.sleep(sleeptime)
        TOPAS.closeShutter()
        wavelengths = np.array(wavelengths)
        intensities = np.array(intensities)
        save.savespectraSFG(ID = gui_instance.sampleID, Inttime = gui_instance.intt, OPALambda = gui_instance.wavel, Position = pos, Wavelengths = darkwavelengths, Intensities = darkintensities, DarkSpectra = False)
        return wavelengths, intensities