import tkinter as tk
import numpy as np
import time
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seabreeze														#spectrometer
from seabreeze.spectrometers import list_devices, Spectrometer


cond = False 
data = np.array([])
root = tk.Tk()
root.title('Real Time Datacquisition')
root.configure(background = 'light blue')
root.geometry('900x500')

##### create plot object on GUI #####

fig = Figure()
ax = fig.add_subplot(1,2,1)
ax.set_title('')
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_xlim(0,100)
ax.set_ylim(-0.5,1000)
lines = ax.plot([],[])[0]												#gives an array in whcih we can set x and y data later on to have astatic axes window
array = np.linspace(0,100,100)
enum = list(enumerate(array))
random.shuffle(enum)
print(enum[1][0])
print(enum[1][1])

print(len(enum))

x = np.linspace(-10,10,10) #distribution
y = np.linspace(266, 1057, 10)#wavelengths
z = np.array([random.randint(0,1) for j in x for i in y])
Z = z.reshape(len(y), len(x))
z2 = np.array([i*j+j*j for j in x for i in y])
z3 = np.array([random.random() for j in x for i in y])

Z2 = z2.reshape(len(y), len(x))
Z3 = z3.reshape(len(y), len(x))

ax2 = fig.add_subplot(1,2,2)
lines2 = ax2.imshow(Z2, interpolation='nearest', 
                            #origin='lower', 
                            extent=[min(x),max(x),min(y),max(y)],
                            aspect='auto', # get rid of this to have equal aspect 
                            cmap='jet')
                            #vmin = 0,
                            #vmax = 1000)
#lines2 = ax2.pcolormesh(X,Y,Z)
#fig.colorbar(lines2)

cbar = fig.colorbar(lines2)

canvas = FigureCanvasTkAgg(fig, master = root)
canvas.get_tk_widget().place(x=10,y=10, width = 600, height = 400)
canvas.draw()

##### create buttons #####
root.update()
start = tk.Button(root, text = 'Start measurement', font = ('calibri',12), command = lambda: plot_start())
start.place(x = 650, y = 300)

#root.update()
#stop = tk.Button(root, text = 'Stop measurement', font = ('calibri',12), command = lambda: plot_stop())
#stop.place(x = 650, y = start.winfo_x()+start.winfo_reqheight()+20)

root.update()
NumDataPoints = tk.Entry(root)
NumDataPoints.place(x = 650, y = 50)

root.update()
OKButton = tk.Button(root, text = 'Eingabe bestaetigen', command = lambda: read_input_field())
OKButton.place(x = 650, y = 100)

def plot_data(root):
	global cond, data, i, Z
	i = 0
	x = np.linspace(-5,5,100) #distribution
	y = np.linspace(266, 1057, 1044)#wavelengths
	z = np.array([random.randint(0,1) for j in x for i in y])
	Z = z.reshape(len(y), len(x))
	def inner_func():
		global i, cond, data, Z
		maxiteration = 100
		if (cond == True and i < maxiteration):
			data = np.ones(1044)*random.randint(10,1000)
			lines.set_xdata(np.arange(0,len(data)))
			lines.set_ydata(data)
			Z[:,enum[i][0]] = np.ones(1044)*enum[i][1]
			lines2.set_data(Z)
			lines2.set_clim(vmin=0,vmax=np.amax(Z))
			canvas.draw()
			i = i+1
		root.after(100,inner_func)
	inner_func()

def plot_start():
	global cond
	cond = True

def plot_stop():
	global cond
	cond = False
def read_input_field():
	current_input = NumDataPoints.get()
	print(current_input)
	
	
#def create_new_spectra():
#	global data
#	for x in range(50): 
#		#data = np.ones(1044)*random.randint(10,1000)
#		root.after(100,plot_data)
#		time.sleep(1)

root.after(100,plot_data(root))
root.mainloop()