def acquire(gui_instance,TOPAS, SPECTROM, RSTAGE):
    if int(gui_instance.intt) < max(SPECTROM.integration_time_micros_limits):
        SPECTROM.integration_time_micros(int(gui_instance.intt))
    TOPAS.openShutter()
    RSTAGE.move_absolute_mm(10, waitStop=False)
    while gui_instance.LiveSpecCond:
        wavelengths, intensities = SPECTROM.spectrum(correct_dark_counts=False)
        gui_instance.lines1.set_xdata(wavelengths)
        gui_instance.lines1.set_ydata(intensities)
        gui_instance.ax1.set_ylim(-1e3,max(intensities)+1e3)
        gui_instance.parent.after(100, gui_instance.canvas_update)
        gui_instance.parent.update_idletasks()
    TOPAS.closeShutter()

