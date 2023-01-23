import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import colors
from math import floor,ceil
import numpy as np
import random
import threading
import Colormap_acquire_new as Cmap
import Live_spectra_measurement as Lspec

class GUI(tk.Frame):
	
	def __init__(self, parent, *args):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.StartCond = False
		self.LiveSpecCond = False
		self.InputParamCond = False
		self.autoint = False
		self.sampleID = "None"
		if len(args) == 3:
			self.TOPAS = args[0]
			self.SPECTROMETER = args[1]
			self.ROTATIONSTAGE = args[2]
	
	def setup(self):
		colortheme = 'gray90'
		self.parent.configure(background = colortheme)
		self.parent.geometry('1000x820')
		self.parent.title ('Colormap Measurement') # give
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
		self.x = np.linspace(1200,2400,40)#distribution
		self.y = np.linspace(266, 1057, 2)#wavelengths
		self.z = np.array([random.randint(0,1) for j in self.x for i in self.y])
		self.Z = self.z.reshape(len(self.y), len(self.x))

		self.lines2 = self.ax2.imshow(self.Z, interpolation='nearest', norm=colors.LogNorm(),
									#origin='lower', 
								extent=[min(self.x),max(self.x),min(self.y),max(self.y)], # hier anpassen
								aspect='auto', # get rid of this to have equal aspect 
								cmap='jet')
		#self.cbar = self.fig.colorbar(self.lines2)
		self.ax2.set_title('SFG Colormap')
		self.ax2.set_xlabel('Fund. Wavelength [nm]')
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

		self.ConfigDropdownText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.ConfigDropdownText.place(x = 850, y = 25)
		self.ConfigDropdownText.insert('end', 'Interaction')
		self.ConfigDropdown = tk.OptionMenu(self.parent , self.ConfigMenu , *self.options )
		self.ConfigDropdown.place(x = 850, y = 50)

		self.InttimeText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.InttimeText.place(x = 850, y = 100)
		self.InttimeText.insert('end', 'Inttime (us)')
		self.InttimeText.config(state='disabled')
		self.Inttime = tk.Entry(self.parent)
		self.Inttime.place(x = 850, y = 125)
		self.InttimeTextOut= tk.Text(self.parent,height=1,width=15)
		self.InttimeTextOut.place(x = 850, y = 150)
		self.InttimeTextOut.insert('end', 'SET: NONE')

		self.WavelengthMinText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.WavelengthMinText.place(x = 850, y = 200)
		self.WavelengthMinText.insert('end', 'Min Wavel (nm)')
		self.WavelengthMinText.config(state='disabled')
		self.WavelengthMin = tk.Entry(self.parent)
		self.WavelengthMin.place(x = 850, y = 225)
		self.WavelengthMinTextOut= tk.Text(height=1,width=15)
		self.WavelengthMinTextOut.place(x = 850, y = 250)
		self.WavelengthMinTextOut.insert('end', 'SET: NONE')

		self.WavelengthMaxText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.WavelengthMaxText.place(x = 850, y = 300)
		self.WavelengthMaxText.insert('end', 'Max Wavel (nm)')
		self.WavelengthMaxText.config(state='disabled')
		self.WavelengthMax = tk.Entry(self.parent)
		self.WavelengthMax.place(x = 850, y = 325)
		self.WavelengthMaxTextOut= tk.Text(height=1,width=15)
		self.WavelengthMaxTextOut.place(x = 850, y = 350)
		self.WavelengthMaxTextOut.insert('end', 'SET: NONE')

		self.WLIncrementText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.WLIncrementText.place(x = 850, y = 400)
		self.WLIncrementText.insert('end', 'Increment (nm)')
		self.WLIncrementText.config(state='disabled')
		self.WLIncrement = tk.Entry(self.parent)
		self.WLIncrement.place(x = 850, y = 425)
		self.WLIncrementTextOut= tk.Text(self.parent,height=1,width=15)
		self.WLIncrementTextOut.place(x = 850, y = 450)
		self.WLIncrementTextOut.insert('end', 'SET: NONE')

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

		self.LiveSpectraButton = tk.Button(self.parent, text = 'Live Spectra',height = 1, width = 15, bg='gray60', command = lambda: self.LiveSpectra())
		self.LiveSpectraButton.place(x = 450, y = 25)

		self.AutoIntButton = tk.Button(self.parent, text = 'AutoInt', font = ('calibri',12), bg='red', command = lambda: self.changeAutoIntStatus())
		self.AutoIntButton.place(x = 850, y = 760)
		self.AutoIntButton.config(width = 15,height = 2)

		self.RemainingTimeText = tk.Text(self.parent,height=1,width=15, bg = colortheme)
		self.RemainingTimeText.place(x = 650, y = 25)
		self.RemainingTimeText.insert('end', 'Remaining time')
		self.RemainingTimeText.config(state='disabled')
		self.RemainingTimeTextOut= tk.Text(height=1,width=15)
		self.RemainingTimeTextOut.place(x = 650, y = 50)
		self.RemainingTimeTextOut.insert('end', 'NONE')


		self.parent.update()
		
	def plot_start(self):	
		self.StartCond = True
		if (self.InputParamCond and not self.LiveSpecCond):
			self.StartCond = True
			self.disable_buttons()
			self.Meas_thread = threading.Thread(target = Cmap.start_measurement, args = (self, self.TOPAS, self.SPECTROMETER, self.ROTATIONSTAGE,))
			self.Meas_thread.start()	
		elif not self.InputParamCond:
			print("Invalid input parameters")
		elif self.LiveSpecCond:
			print("Live spectra running!")

	def disable_buttons(self):
		self.ConfigDropdown.config(state="disabled")
		self.Shutter.config(state="disabled")
		self.start.config(state="disabled")
		self.OKButton.config(state="disabled")
		self.LiveSpectraButton.config(state="disabled")
		
	def enable_buttons(self):
		self.ConfigDropdown.config(state="normal")
		self.Shutter.config(state="normal")
		self.start.config(state="normal")
		self.OKButton.config(state="normal")
		self.LiveSpectraButton.config(state="normal")

	def plot_stop(self):
		self.StartCond = False
		
	def read_input_fields(self):
		self.InputParamCond = True
		self.wavel = None
		self.intt = None
		self.numdp = None
		self.config = None
		
		self.interaction_ranges = [[630, 1020],[640, 940],[1032,2762],[1129, 2585],[640,940],[1129,2585]] #SIG LONG [0] , SIG [1], IDL LONG [2], IDL [3], CMP-SIG [4], CMP-IDL [5]
		self.inttime_limits = [1e4, 1e7]
		self.increment_limits = [10, 200]
		self.max_inttime = self.inttime_limits[1] 
		self.options = ["SIG LONG", "SIG", "IDL LONG", "IDL", "CMP-SIG", "CMP-IDL"]
		try:
			
			self.config = str(self.ConfigMenu.get())
			self.config_num = self.options.index(self.config)
	
			self.intt = int(self.Inttime.get())
			if not (self.intt > self.inttime_limits[0] and self.intt < self.inttime_limits[1]):
				self.InputParamCond = False
				print("Set inttime is out of bounds [%i - %i]" % (self.inttime_limits[0]+1,self.inttime_limits[1]-1))
			else:
				self.InttimeTextOut.delete('1.0', 'end')
				self.InttimeTextOut.insert('end', str(self.intt) + ' us')
			
			self.increment = int(self.WLIncrement.get())
			if not (self.increment >= self.increment_limits[0] and self.increment <= self.increment_limits[1]):
				self.InputParamCond = False
				print("Set Increment is out of bounds [%i - %i]" % (self.increment_limits[0],self.increment_limits[1]))
			else:
				self.WLIncrementTextOut.delete('1.0', 'end')
				self.WLIncrementTextOut.insert('end', str(self.increment))

			self.wavelmin = int(self.WavelengthMin.get())
			self.wavelmax = int(self.WavelengthMax.get())
			if not (self.wavelmin > self.interaction_ranges[self.config_num][0] and self.wavelmax < self.interaction_ranges[self.config_num][1]):
				self.InputParamCond = False
				print("Set Wavelength Limits out of bounds [%i - %i]" % (self.interaction_ranges[self.config_num][0]+1,self.interaction_ranges[self.config_num][1]-1))
			else:
				if ((self.wavelmin - self.wavelmax) > self.increment):
					self.InputParamCond = False
					print("Set Increment and Range don't match")
				else:
					self.WavelengthMinTextOut.delete('1.0', 'end')
					self.WavelengthMinTextOut.insert('end', str(self.wavelmin) + ' nm')
					self.WavelengthMaxTextOut.delete('1.0', 'end')
					self.WavelengthMaxTextOut.insert('end', str(self.wavelmax) + ' nm')
					bot = ceil(self.wavelmin/self.increment)
					top = floor(self.wavelmax/self.increment)

					self.wavelengths = self.increment*np.array(list(range(bot, top+1)))
					print("The Following wavelengths are covered: ")
					print(self.wavelengths)

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

	def changeAutoIntStatus(self):
		self.autoint = not self.autoint
		if self.autoint:
			self.AutoIntButton.config(bg = 'green')
		else:
			self.AutoIntButton.config(bg = 'red')

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

	def canvas_update(self):
		self.canvas.draw()

	def LiveSpectra(self):
		if self.LiveSpecCond:
			self.stop_live_spectra()
		elif self.InputParamCond:
			self.start_live_spectra()
		else:
			print("Live Spectra: Invalid input parameters")

	def start_live_spectra(self):
		self.LiveSpecCond = True
		self.LiveSpectraButton.config(bg = 'magenta2')
		self.LiveSpec_thread = threading.Thread(target = Lspec.acquire, args = (self, self.TOPAS, self.SPECTROMETER, self.ROTATIONSTAGE))
		self.LiveSpec_thread.start()
			
	def stop_live_spectra(self):
		self.LiveSpecCond = False	
		self.LiveSpectraButton.config(bg = 'gray60')


if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    gui.setup()
    root.mainloop()
