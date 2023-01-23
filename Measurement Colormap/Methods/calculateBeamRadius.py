import numpy as np
def BeamRadius(Lambda, FocalDistance, BeamRadiusLense, M, z):
    w = Lambda*FocalDistance*np.power(M,2)/(np.pi*BeamRadiusLense)*np.sqrt(1 + np.power(z*np.pi*np.power(BeamRadiusLense,2)/(Lambda*np.power(FocalDistance*M,2)),2)) 
    return w
