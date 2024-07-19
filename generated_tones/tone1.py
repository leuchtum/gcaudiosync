from pathlib import Path

import numpy as np
from gen import (
    Interval,
    gen_chirp_wave,
    gen_sawtooth_wave,
    gen_sine_wave,
    gen_square_wave,
    gen_triangle_wave,
    gen_white_noise,
    write_wav,
)

# Total Interval
TOTAL_DURATION = 12
i_tot = Interval(0, TOTAL_DURATION)

# Buffer
buf = np.zeros(i_tot.nsamples)

# Some noise
buf[i_tot.slice_] += 0.2 * gen_sine_wave(50, i_tot)
buf[i_tot.slice_] += 0.3 * gen_white_noise(i_tot)

# The fingerprints
i = Interval(0.5, 1)
buf[i.slice_] += gen_sine_wave(600, i)
i = Interval(11, 11.5)
buf[i.slice_] += gen_sine_wave(600, i)

# Some tones
freq = 800
i = Interval(2, 3)
buf[i.slice_] += gen_sine_wave(freq, i)
i = Interval(3, 4)
buf[i.slice_] += gen_triangle_wave(freq, i)
i = Interval(4, 5)
buf[i.slice_] += gen_sawtooth_wave(freq, i)
i = Interval(5, 6)
buf[i.slice_] += gen_square_wave(freq, i)

i = Interval(7, 8)
buf[i.slice_] += gen_chirp_wave(100, 1000, i)
i = Interval(8, 9.05)
buf[i.slice_] += gen_sine_wave(1000, i)
i = Interval(9, 10)
buf[i.slice_] += gen_chirp_wave(1000, 100, i)


# Normalize the buffer
buf /= np.max(np.abs(buf))

# Save the buffer as a WAV file
file = Path(__file__).with_suffix(".wav")
write_wav(file, buf)
