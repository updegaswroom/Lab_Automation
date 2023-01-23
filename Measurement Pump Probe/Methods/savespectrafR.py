from datetime import datetime
import os
from seabreeze.spectrometers import list_devices, Spectrometer			
import Directory_setup as directory


def savespectrafR(ID = None, Inttime = None, OPALambda = None,DeltaT = None, Power = None,Wavelengths = None, Intensities = None, DarkSpectra = False, silent = True):

		#create folder for fundamental lambda!
		#add measurement iteration number?
		xs = Wavelengths
		ys = Intensities
		inttime = Inttime
		power = Power
		sampleID = ID
		dateTimeObj = datetime.now()
		timestamp = dateTimeObj.strftime("%Y_%m_%d__%H_%M_%S")
		date = dateTimeObj.strftime("%Y%m%d")
		cwd = os.getcwd() # current working directory --> directory of __main__ script location
		checkpath = os.path.join(cwd,"Pump Probe Measurements",date,ID,str(OPALambda))
		if not directory.check_for_dir(checkpath,silent):
			pathmeas = directory.create_new_dir(cwd,"Pump Probe Measurements")
			pathday = directory.create_new_dir(pathmeas,date)
			intpath = directory.create_new_dir(pathday,ID)
			finpath = directory.create_new_dir(intpath,str(OPALambda),silent)
		else:
			finpath = checkpath
		filesuffix = ".txt"
		if DarkSpectra:
			filename = f"HarmRatio_{sampleID}_{timestamp}_{str(DeltaT)}ps_dark{filesuffix}"
		else:
			filename = f"HarmRatio_{sampleID}_{timestamp}_{str(DeltaT)}ps{filesuffix}"
		filepath = os.path.join(finpath,filename)  #backslash for separation?
		
		
		with open(filepath, 'w') as f:
			timestamp = dateTimeObj.strftime("%Y %m %d (%H-%M-%S)")
			power = '{:d}'.format(int(power))
			integrationtime = '{:d}'.format(int(inttime/1000))
			f.write(f"Date: {timestamp} ) \n")
			f.write(f"Wavelength: {str(OPALambda)} nm \n")
			f.write(f"RawPower: {power} mW \n")
			f.write(f"RealPower: {str(int(power)*10)} mW \n")
			f.write(f"Inttime: {integrationtime} ms \n")
			f.write(f"DeltaT: {DeltaT} ps \n")
			for index in range(len(xs)):
				f.write("%d" % xs[index])
				f.write("\t")
				f.write("%d" % ys[index])
				f.write("\n")

def testrun():
	inttime = 10000
	#SPECTROMETER = Spectrometer.from_first_available()						#find and connect to available spectrometer
	#if inttime < max(SPECTROMETER.integration_time_micros_limits): 					#check if the set integration time is in a valid range
	#	SPECTROMETER.integration_time_micros(inttime)
	
	#darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False) 
	darkwavelengths = []
	darkintensities = []
	savespectrafR(ID = "TESTSAMPLE", Inttime = inttime, OPALambda = "1300",DeltaT = "10", Power = "30", Wavelengths = darkwavelengths, Intensities = darkintensities)

if __name__ == "__main__":
	testrun()
