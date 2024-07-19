from pathlib import Path

import numpy as np
from gen import (
    Interval,
    gen_chirp_wave,
    gen_sine_wave,
    gen_white_noise,
    write_wav,
)


def gen_ramp_up_ramp_down_tone(buffer, start, freq, durations):
    ramp_up = Interval(start, start + durations[0])
    inner = Interval(ramp_up.end, ramp_up.end + durations[1])
    ramp_down = Interval(inner.end, inner.end + durations[2])

    buffer[ramp_up.slice_] += gen_chirp_wave(0, freq, ramp_up)
    buffer[inner.slice_] += gen_sine_wave(freq, inner)
    buffer[ramp_down.slice_] += gen_chirp_wave(freq, 0, ramp_down)


# Gesamtintervalle
TOTAL_DURATION = 15  # Sekundäre Dauer des gesamten Audios
i_tot = Interval(0, TOTAL_DURATION)

# Initialisiere den Buffer
buf = np.zeros(i_tot.nsamples)

# Noise hinzufügen
buf += 0.1 * gen_white_noise(i_tot)


# Fingeprint 600Hz
gen_ramp_up_ramp_down_tone(buf, 1, 600, [0.2, 0.6, 0.2])


# Verschiedene Frequenzen mit Übergang
freqs = [300, 400, 500, 700, 800]
start = 3
for freq in freqs:
    durations = [0.4, 1.2, 0.4]
    gen_ramp_up_ramp_down_tone(buf, start, freq, durations)
    start += sum(durations)


# Fingeprint 600Hz
gen_ramp_up_ramp_down_tone(buf, start, 600, [0.2, 0.6, 0.2])

# Normalisierung des Buffers
buf /= np.max(np.abs(buf))

# Speichern des Buffers als WAV-Datei
file = Path(__file__).with_suffix(".wav")
write_wav(file, buf)
