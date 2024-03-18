import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

# Import the .wav audio
f = "/Users/daniel/Desktop/WD_cse_project/NC-Simulation/VID_20240103_125230_MONO.wav"

# s = sampling (int)
# a = audio signal (numpy array)

s, a = wavfile.read(f)
print("Sampling Rate:", s)
print("Audio Shape:", np.shape(a))

# number of samples
na = a.shape[0]
# audio time duration
la = na / s

# plot signal versus time
t = np.linspace(0, la, na)
plt.plot(t, a, "b-")
plt.xlabel("Time (s)")
plt.show()

plt.show()


a
