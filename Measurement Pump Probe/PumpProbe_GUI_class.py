import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from math import floor,ceil
import numpy as np
import random
import threading
import PumpProbe_acquire_new as PumpProbe

class GUI(tk.Frame):
	
	def __init__(self, parent, *args):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.StartCond = False
		self.InputParamCond = False
		self.MeasuringStatus = True
		self.disp_wavelengths = None
		self.sampleID = "None"
		self.DispersionStatus = False
		if len(args) == 3:
			self.TOPAS = args[0]
			self.SPECTROMETER = args[1]
			self.ROTATIONSTAGE = args[2]
	
	def setup(self):
		colortheme = 'gray90'
		self.parent.configure(background = colortheme)
		self.parent.geometry('1000x820')
		self.parent.title('Pump Probe Measurement') # give
		##### create plot object on GUI #####
		plt.style.use('default')
		self.fig = Figure()
		self.fig.patch.set_facecolor([0.9, 0.9, 0.9])
		self.ax1 = self.fig.add_subplot(1,2,1)
		self.ax1.set_title('Spectrometer')
		self.ax1.set_xlabel('Wavelength [nm]')
		self.ax1.set_ylabel('Counts [a.u.]')
		self.ax1.set_xlim(266,1057)
		self.ax1.set_ylim(-500,2e4)
		self.lines1 = self.ax1.plot([],[])[0]	

		self.ax2 = self.fig.add_subplot(1,2,2)
		self.x = np.linspace(-10,10,10) #distribution
		self.y = np.linspace(266, 1057, 10)#wavelengths
		self.z = np.array([random.randint(0,1) for j in self.x for i in self.y])
		self.Z = self.z.reshape(len(self.y), len(self.x))

		self.lines2 = self.ax2.imshow(self.Z, interpolation='nearest', 
									#origin='lower', 
								extent=[min(self.x),max(self.x),min(self.y),max(self.y)],
								aspect='auto', # get rid of this to have equal aspect 
								cmap='jet')
		#self.cbar = self.fig.colorbar(self.lines2)
		self.ax2.set_title('SFG Colormap')
		self.ax2.set_xlabel('Time Delay [ps]')
		self.ax2.set_ylabel('Wavelength [nm]')
		self.ax2.set_xlim(min(self.x),max(self.x))
		self.ax2.set_ylim(min(self.y),max(self.y))

		self.ax1.set_position([0.13, 0.56, 0.8, 0.32])
		self.ax2.set_position([0.13, 0.14, 0.8, 0.32])

		self.canvas = FigureCanvasTkAgg(self.fig, master = self.parent)
		self.canvas.get_tk_widget().place(x=10,y=10, width = 800, height = 800)
		self.canvas.draw()

		self.options = [
			"SIG LONG",
			"SIG",
			"IDL LONG",
			"IDL",
			"CMP-SIG",
			"CMP-IDL"]
	
		self.ConfigMenu = tk.StringVar()
		self.ConfigMenu.set(self.options[5])

		self.Shutter = tk.Button(self.parent, text = 'SHUTTER', font = ('calibri',12), bg='gray60', command = lambda: self.changeShutter())
		self.Shutter.place(x = 50, y = 10)
		self.Shutter.config(width = 15,height = 2)

		"""
		self.OPAwavelength = tk.Text(self.parent, height=1,width=20, font = ('calibri',12), bg = colortheme)
		self.OPAwavelength.place(x = 200, y = 10)
		self.OPAwavelength.insert(1.0, "CMP-IDL: WAVELENGTH (nm)")
		self.OPAwavelength.tag_configure("center", justify='center')
		self.OPAwavelength.tag_add("center", "1.0", "end")
		self.OPAwavelength.config(width = 35,height = 2)
		"""

		self.ConfigDropdownText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.ConfigDropdownText.place(x = 850, y = 25)
		self.ConfigDropdownText.insert('end', 'Interaction')
		self.ConfigDropdown = tk.OptionMenu(self.parent , self.ConfigMenu , *self.options )
		self.ConfigDropdown.place(x = 850, y = 50)

		self.WavelengthText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.WavelengthText.place(x = 850, y = 100)
		self.WavelengthText.insert('end', 'Wavelength (nm)')
		self.WavelengthText.config(state='disabled')
		self.Wavelength = tk.Entry(self.parent)
		self.Wavelength.place(x = 850, y = 125)
		self.WavelengthTextOut= tk.Text(height=1,width=15)
		self.WavelengthTextOut.place(x = 850, y = 150)
		self.WavelengthTextOut.insert('end', 'SET: NONE')

		self.InttimeText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.InttimeText.place(x = 850, y = 200)
		self.InttimeText.insert('end', 'Inttime (us)')
		self.InttimeText.config(state='disabled')
		self.Inttime = tk.Entry(self.parent)
		self.Inttime.place(x = 850, y = 225)
		self.InttimeTextOut= tk.Text(self.parent,height=1,width=15)
		self.InttimeTextOut.place(x = 850, y = 250)
		self.InttimeTextOut.insert('end', 'SET: NONE')

		self.RangeOfDelayText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.RangeOfDelayText.place(x = 850, y = 300)
		self.RangeOfDelayText.insert('end', 'Time Range (ps)')
		self.RangeOfDelayText.config(state='disabled')
		self.RangeOfDelay = tk.Entry(self.parent)
		self.RangeOfDelay.place(x = 850, y = 325)
		self.RangeOfDelayTextOut= tk.Text(self.parent,height=1,width=15)
		self.RangeOfDelayTextOut.place(x = 850, y = 350)
		self.RangeOfDelayTextOut.insert('end', 'SET: NONE')

		self.NumDataPointsText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.NumDataPointsText.place(x = 850, y = 400)
		self.NumDataPointsText.insert('end', '#Datapoints')
		self.NumDataPointsText.config(state='disabled')
		self.NumDataPoints = tk.Entry(self.parent)
		self.NumDataPoints.place(x = 850, y = 425)
		self.NumDataPointsTextOut= tk.Text(self.parent,height=1,width=15)
		self.NumDataPointsTextOut.place(x = 850, y = 450)
		self.NumDataPointsTextOut.insert('end', 'SET: NONE')

		self.SampleName = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.SampleName.place(x = 850, y = 500)
		self.SampleName.insert('end', 'Sample ID')
		self.SampleName.config(state='disabled')
		self.SampleID = tk.Entry(self.parent)
		self.SampleID.place(x = 850, y = 525)
		self.SampleNameOut= tk.Text(self.parent,height=1,width=15)
		self.SampleNameOut.place(x = 850, y = 550)
		self.SampleNameOut.insert('end', 'SET: NONE')

		self.OKButton = tk.Button(self.parent, text = 'Confirm values',height = 1, width = 16, command = lambda: self.read_input_fields())
		self.OKButton.place(x = 850, y = 575)

		self.start = tk.Button(self.parent, text = 'Start',height = 2, width = 15, font = ('calibri',12), bg='green', command = lambda: self.plot_start())
		self.start.place(x = 850, y = 620)

		self.stop = tk.Button(self.parent, text = 'Abort',height = 2, width = 15, font = ('calibri',12), bg='red', command = lambda: self.plot_stop())
		self.stop.place(x = 850, y = 700)

		self.RemainingTimeText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.RemainingTimeText.place(x = 650, y = 25)
		self.RemainingTimeText.insert('end', 'Remaining time')
		self.RemainingTimeText.config(state='disabled')
		self.RemainingTimeTextOut= tk.Text(height=1,width=15)
		self.RemainingTimeTextOut.place(x = 650, y = 50)
		self.RemainingTimeTextOut.insert('end', 'NONE')

		self.DispersionButton = tk.Button(self.parent, text = 'Dispersion', font = ('calibri',12), bg='red', command = lambda: self.changeDispersionStatus())
		self.DispersionButton.place(x = 850, y = 760)
		self.DispersionButton.config(width = 15,height = 2)

		self.parent.update()
		
	def plot_start(self):	
		self.StartCond = True
		if self.InputParamCond == True:
			self.StartCond = True
			self.disable_buttons()
			#fR.startMeasurement(self, *self.read_input_fields(), self.TOPAS, self.SPECTROMETER, self.ROTATIONSTAGE)
			#self.parent.after(100,fR.startMeasurement, self, *self.read_input_fields(), self.TOPAS, self.SPECTROMETER, self.ROTATIONSTAGE)
			#self.parent.after(100,fR.startMeasurement, self, 5)
			#Meas_thread = threading.Thread(target = fR.startMeasurement, args = (self,5,))
			Meas_thread = threading.Thread(target = PumpProbe.startMeasurement, args = (self, *self.read_input_fields(), self.TOPAS, self.SPECTROMETER, self.ROTATIONSTAGE,))
			Meas_thread.start()	
		else:
			print("Invalid input parameters")

	def disable_buttons(self):
		self.DispersionButton.config(state="disabled")
		self.ConfigDropdown.config(state="disabled")
		self.Shutter.config(state="disabled")
		self.start.config(state="disabled")
		self.OKButton.config(state="disabled")

	def enable_buttons(self):
		self.DispersionButton.config(state="normal")
		self.ConfigDropdown.config(state="normal")
		self.Shutter.config(state="normal")
		self.start.config(state="normal")
		self.OKButton.config(state="normal")

	def plot_stop(self):
		self.StartCond = False
		
	def read_input_fields(self):
		self.InputParamCond = True
		self.wavel = None
		self.intt = None
		self.numdp = None
		self.rangeDT = None
		self.config = None
		
		self.interaction_ranges = [[630, 1020],[640, 940],[1032,2762],[1129, 2585],[640,940],[1129,2585]] #SIG LONG [0] , SIG [1], IDL LONG [2], IDL [3], CMP-SIG [4], CMP-IDL [5]
		self.inttime_limits = [1e4, 1e7]
		self.datapoints_limits = [10, 1000]
		self.rangeDT_limits = [0.1, 10]
		self.options = ["SIG LONG", "SIG", "IDL LONG", "IDL", "CMP-SIG", "CMP-IDL"]
		try:
			
			self.config = str(self.ConfigMenu.get())
			self.config_num = self.options.index(self.config)
	
			self.wavel = int(self.Wavelength.get())
			if not (self.wavel > self.interaction_ranges[self.config_num][0] and self.wavel < self.interaction_ranges[self.config_num][1]):
				self.InputParamCond = False
				#win32gui.MessageBox(0,'Set wavelength is out of bounds ', '', 0)
				print("Set inttime is out of bounds [%i - %i]" % (self.interaction_ranges[self.config_num][0]+1,self.interaction_ranges[self.config_num][1]-1))
			else:
				self.WavelengthTextOut.delete('1.0', 'end')
				self.WavelengthTextOut.insert('end', str(self.wavel) + ' nm')
				
			self.intt = int(self.Inttime.get())
			if not (self.intt > self.inttime_limits[0] and self.intt < self.inttime_limits[1]):
				self.InputParamCond = False
				#win32gui.MessageBox(0,'Set inttime is out of bounds ', '', 0)
				print("Set inttime is out of bounds [%i - %i]" % (self.inttime_limits[0]+1,self.inttime_limits[1]-1))
			else:
				self.InttimeTextOut.delete('1.0', 'end')
				self.InttimeTextOut.insert('end', str(self.intt) + ' us')
			
			self.rangeDT = float(self.RangeOfDelay.get())

			if not (self.rangeDT >= self.rangeDT_limits[0] and self.rangeDT <= self.rangeDT_limits[1]):
				self.InputParamCond = False
				print("Set datapoint number is out of bounds [%.1f - %.1f]" % (self.rangeDT_limits[0],self.rangeDT_limits[1]))
			else:
				self.RangeOfDelayTextOut.delete('1.0', 'end')
				self.RangeOfDelayTextOut.insert('end', str(self.rangeDT))

			self.numdp = int(self.NumDataPoints.get())
			if not (self.numdp > self.datapoints_limits[0] and self.numdp < self.datapoints_limits[1]):
				self.InputParamCond = False
				print("Set datapoint number is out of bounds [%i - %i]" % (self.datapoints_limits[0]+1,self.datapoints_limits[1]-1))
			else:
				self.NumDataPointsTextOut.delete('1.0', 'end')
				self.NumDataPointsTextOut.insert('end', str(self.numdp))

			self.sampleID = str(self.SampleID.get())
			self.SampleNameOut.delete('1.0', 'end')
			self.SampleNameOut.insert('end', str(self.sampleID))

		except ValueError:
			self.InputParamCond = False
			print('Insertet values are not integers')
			
		return self.config, self.wavel, self.numdp, self.sampleID

	def changeShutter(self):
		self.TOPAS.changeShutter()
		color, status = self.setShutterStatusInfo()
		self.Shutter.config(text = status, bg = color)

	def resetAfterMeasurement(self):
		self.StartCond = False
		self.InputParamCond = False
		self.enable_buttons()

	def getShutterStatus(self):
		return self.TOPAS.getShutterStatus()
	
	def setShutterStatusInfo(self):
		if not self.getShutterStatus():
			return 'magenta2','OPEN'
		else: 
			return 'gray60','CLOSED'

	def changeDispersionStatus(self):
		self.DispersionStatus = not self.DispersionStatus
		if self.DispersionStatus:
			self.DispersionButton.config(bg = 'green')
		else:
			self.DispersionButton.config(bg = 'red')

	def setDispersionRange(self, base = 50, lower_limit = None, upper_limit = None):
		#finish this method to accept valid inputs --> value control has to be done in upper call_var method
		if lower_limit == None or upper_limit == None:
			lower_limit = self.interaction_ranges[self.config_num][0]
			upper_limit = self.interaction_ranges[self.config_num][1]

		lower_wl = ceil(lower_limit/base)*base
		upper_wl = floor(upper_limit/base)*base
		numpoints = np.abs(upper_wl - lower_wl)/base + 1
		self.disp_wavelengths = np.linspace(lower_wl, upper_wl, int(numpoints))

	def canvas_update(self):
		self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    gui.setup()
    root.mainloop()
