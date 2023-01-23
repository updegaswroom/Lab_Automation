import numpy as np
import matplotlib.pyplot as plt

#np.savetxt('Lambda_Reflection_CMP-IDL.txt', LR, fmt='%d')
LR = np.loadtxt('Lambda_Reflection_CMP-IDL.txt', dtype=int)
#np.savetxt('Lambda_Transmission_CMP-IDL.txt', LT, fmt='%d')
LT = np.loadtxt('Lambda_Transmission_CMP-IDL.txt', dtype=int)
#np.savetxt('Transmission_CMP-IDL.txt', T, fmt='%f5')
T = np.loadtxt('Transmission_CMP-IDL.txt', dtype=float)
#np.savetxt('Reflection_CMP-IDL.txt', R, fmt='%f5')
R = np.loadtxt('Reflection_CMP-IDL.txt', dtype=float)

Reflection_perc =  (T[:]/R[:])
Refl = Reflection_perc[:]*R[:]


print(Refl)
print(LR)
plt.plot(LT,T*1000)
plt.plot(LR,R*1000)
plt.plot(LR,Refl*1000)
plt.show()