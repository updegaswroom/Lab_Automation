import numpy as np
import matplotlib.pyplot as plt

"""
np.savetxt('Lambda_Reflection_CMP-IDL.txt', LR, fmt='%d')
np.savetxt('Reflection_CMP-IDL.txt', R, fmt='%f5')
np.savetxt('Lambda_Transmission_CMP-IDL.txt', LT, fmt='%d')
np.savetxt('Transmission_CMP-IDL.txt', T, fmt='%f5')
"""


def CalcSamplePower_setup():
    """Loads Data from Transmission and Reflection Measurement on a 20um objetive slide
     and interpolates to 1 nm steps. Calculates the Conversion Factor to determine Transmitted Power from Reflected Power"""
    LR = np.loadtxt('Lambda_Reflection_CMP-IDL.txt', dtype=int)
    LT = np.loadtxt('Lambda_Transmission_CMP-IDL.txt', dtype=int)
    T = np.loadtxt('Transmission_CMP-IDL.txt', dtype=float)
    R = np.loadtxt('Reflection_CMP-IDL.txt', dtype=float)

    L_T_R = np.linspace(min(LT),max(LT), max(LT)-min(LT)+1)
    T_interpolated = np.interp(L_T_R,LT,T)
    R_interpolated =  np.interp(L_T_R,LR,R)
    Reflection_perc =  (T_interpolated[:]/R_interpolated[:])
    """#This is included for testing purposes only
    Refl = Reflection_perc[:]*R_interpolated[:]
    plt.plot(LT,T*1000)
    plt.plot(LR,R*1000)
    plt.plot(L_T_R,Refl*1000,'x')
    plt.show()"""

    return L_T_R, Reflection_perc


def CalcSamplePower(Lambda, MeasPower):
    """Takes Wavlength (nm) and Reflected Power (W) as input parameters 
    and calculates the Transmitted Power (W)"""
    L_T_R, Refl = CalcSamplePower_setup()
    for index, item in enumerate(L_T_R):    
        if item == Lambda:
           SamplePower = MeasPower*Refl[index]
           return SamplePower

if __name__ == '__main__':
    #CalcSamplePower_setup()
    SP = CalcSamplePower(1400,0.05)
    print(SP)