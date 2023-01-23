import Devices.smc100 as rotationstage												#Controler of the rotationstage
import Devices.OrphirPowermeter as PM
import numpy as np
import matplotlib.pyplot as plt
import time
ROTATIONSTAGE = rotationstage.SMC100(1, 'COM3', silent=False)
ROTATIONSTAGE.reset_and_configure()
assert ROTATIONSTAGE.get_status()[0] == 0
ROTATIONSTAGE.home()
print(ROTATIONSTAGE.get_position_mm())
software_home = -20
ROTATIONSTAGE.move_absolute_mm(software_home)
pos = np.linspace(0+software_home,-330 + software_home,20 )
pow = np.zeros(len(pos))
for i in range(len(pos)):
    ROTATIONSTAGE.move_absolute_mm(pos[i])
    pow[i] = PM.getPower_auto()


plt.plot(pos, pow)
plt.show()