import numpy as np

def PeakInt(BeamRadius, PulseDuration, PulsePower, RepRate):
    PulseEnergy = PulsePower/RepRate
    Ip = 2*PulseEnergy/(np.pi*np.power(BeamRadius,2))*np.sqrt(np.log(16)/(np.pi*np.power(PulseDuration,2)))
    return Ip
