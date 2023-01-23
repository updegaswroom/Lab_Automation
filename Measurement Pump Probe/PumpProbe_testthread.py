#from subprocess import getstatusoutput
import time
import numpy as np
import threading

def waitmethod(gui_instance,zeit):
    gui_instance.MeasuringStatus = True
    print('Start waiting')
    time.sleep(zeit)
    gui_instance.MeasuringStatus = False
    print('Stop waiting')

"""def monitor(gui_instance, thread_status):
    if thread_status.is_alive():
        print('alive')
        gui_instance.parent.after(100, monitor, gui_instance, thread_status)
        #gui_instance.parent.after(100)
        #monitor(gui_instance, thread_status)
    else:
        print('dead')"""

def startMeasurement(gui_instance, sleeptime):
    iter = 0
    #gui_instance.ax1.set_ylim(min(y),max(y))
    gui_instance.lines2.set_marker('x')
    gui_instance.lines2.set_linestyle('')

    def inner_loop(sleeptime, iter):
        if (iter <= 10 and gui_instance.StartCond):
            print('Start sleeping')
            time.sleep(0.1)
            print(iter)
            print('Done sleeping')
            thread_status = threading.Thread(target = waitmethod, args = (gui_instance,5,))
            thread_status.start()
            #fettig = gui_instance.parent.after(100, monitor, gui_instance, thread_status)

            #update loop

            #monitor(gui_instance, thread_status)
            thread_status.join()
            #gui_instance.parent.after(1) bringt alleine nichts
            
            y = np.random.rand(100,1)
            x = np.linspace(0,1000, 100)
            gui_instance.lines1.set_xdata(x)
            gui_instance.lines1.set_ydata(y)
            gui_instance.lines2.set_xdata(x)
            gui_instance.lines2.set_ydata(y)
            gui_instance.ax1.set_ylim(min(y),max(y))
            gui_instance.ax2.set_ylim(min(y),max(y))
            gui_instance.parent.after(50, gui_instance.canvas_update)
            iter = iter + 1
            #gui_instance.parent.after(50,inner_loop, sleeptime, iter) # funktioniert in kombi mit join nicht!

            gui_instance.parent.update_idletasks() #bringt was in kombination mit join und unterem aufruf
            inner_loop(sleeptime, iter)
        elif (not gui_instance.StartCond):
            print('Meas aborted')
        else:
            print('Meas done')
    #gui_instance.parent.after(50,inner_loop, sleeptime, iter)
    inner_loop(sleeptime, iter)
    #gui_instance.parent.after(10,inner_loop, sleeptime, iter)
    #def after(self, ms, func=None, *args):
    """Call function once after given time.

    MS specifies the time in milliseconds. FUNC gives the
    function which shall be called. Additional parameters
    are given as parameters to the function call.  Return
    identifier to cancel scheduling with after_cancel."""
    #gitlab
    #root.update() to catch up???