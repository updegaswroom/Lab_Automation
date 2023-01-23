from datetime import datetime
import os
import Directory_setup as directory
import numpy as np

def savespectrafR(ID = None, Inttime = None, OPALambda = None, Power = None,Wavelengths = None, Intensities = None, DarkSpectra = False, silent = True):

		#create folder for fundamental lambda!
		#add measurement iteration number?

		#Raw Data
		wavelength = Wavelengths
		intensity = Intensities

		###
		dateTimeObj = datetime.now()
		timestamp = dateTimeObj.strftime('%Y_%m_%d__%H_%M_%S')
		date = dateTimeObj.strftime('%Y%m%d')
		ID = str(ID)
		#Header Data
		sampleID = 'sample ID: ' + ID + '\n'
		date_header = 'date: ' + date + '\n'
		integration_time = 'integration time: ' + str(Inttime) + ' us \n'
		power = 'power: ' + str(Power) + ' W \n'
		focal_length = 'focal length: ' + str(0) + ' mm \n'
		sample_distance = 'sample distance: ' + str(0) + ' mm \n'
		header = sampleID + date_header + integration_time + power + focal_length + sample_distance

		print(header)
		#create the saving directory
		cwd = os.getcwd() # current working directory --> directory of __main__ script location
		checkpath = os.path.join(cwd,"Colormap Measurements",date,ID,str(OPALambda))
		if not directory.check_for_dir(checkpath,silent):
			path_meas = directory.create_new_dir(cwd,"Colormap Measurements")
			path_day = directory.create_new_dir(path_meas,date)
			int_path = directory.create_new_dir(path_day,ID)
			final_path = directory.create_new_dir(int_path,str(OPALambda),silent)
		else:
			final_path = checkpath
		file_suffix = ".txt"
		if DarkSpectra:
			file_name = f"Spec_{ID}_{timestamp}_dark{file_suffix}"
		else:
			file_name = f"Spec_{ID}_{timestamp}{file_suffix}"
		file_path = os.path.join(final_path,file_name)  #backslash for separation?
		print(file_path)
		np.savetxt(file_path, (wavelength, intensity), header=header, delimiter=',')

def readspectra():
	wavelengths, intensities = np.loadtxt('spectrum.txt', delimiter=',', unpack=True, skiprows=1)

	# Open the file and read the file header
	with open('spectrum.txt', 'r') as f:
		header = f.readline()

	# Split the header into lines and extract the information
	header_lines = header.split('\n')
	sampleID = header_lines[0].split(': ')[1]
	date = header_lines[1].split(': ')[1]
	integration_time = header_lines[2].split(': ')[1]
	power = header_lines[3].split(': ')[1]
	focal_length = header_lines[4].split(': ')[1]
	sample_distance = header_lines[5].split(': ')[1]
	# Convert the arrays to NumPy arrays
	wavelengths = np.array(wavelengths)
	intensities = np.array(intensities)
	print(wavelengths)
	print(intensities)
	print(header_lines)

def testrun():
	inttime = 10000
	#SPECTROMETER = Spectrometer.from_first_available()						#find and connect to available spectrometer
	#if inttime < max(SPECTROMETER.integration_time_micros_limits): 					#check if the set integration time is in a valid range
	#	SPECTROMETER.integration_time_micros(inttime)
	
	#darkwavelengths, darkintensities = SPECTROMETER.spectrum(correct_dark_counts=False) 
	darkwavelengths = [1000, 1200, 1400, 1600]
	darkintensities = [10, 20, 16, 11]
	savespectrafR(ID = "TESTSAMPLE", Inttime = inttime, OPALambda = "1300", Power = "30", Wavelengths = darkwavelengths, Intensities = darkintensities)
	#readspectra()
if __name__ == "__main__":
	testrun()
