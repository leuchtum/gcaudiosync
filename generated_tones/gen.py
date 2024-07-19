from dataclasses import dataclass

import numpy as np
from scipy.io.wavfile import write
from scipy.signal import chirp

SR = 44100


@dataclass
class Interval:
    start: float
    end: float

    @property
    def slice_(self) -> slice:
        idx_start = int(self.start * SR)
        idx_end = idx_start + self.nsamples
        return slice(idx_start, idx_end)

    @property
    def nsamples(self) -> int:
        return int(SR * self.duration)

    @property
    def duration(self) -> float:
        return self.end - self.start


def gen_sine_wave(freq: float, interval: Interval) -> np.ndarray:
    t = np.linspace(0, interval.duration, interval.nsamples)
    return np.sin(2 * np.pi * freq * t)


def gen_sawtooth_wave(freq: float, interval: Interval) -> np.ndarray:
    t = np.linspace(0, interval.duration, interval.nsamples)
    return 2 * (t * freq - np.floor(t * freq + 0.5))


def gen_square_wave(freq: float, interval: Interval) -> np.ndarray:
    t = np.linspace(0, interval.duration, interval.nsamples)
    return 2 * (np.sign(np.sin(2 * np.pi * freq * t)))


def gen_triangle_wave(freq: float, interval: Interval) -> np.ndarray:
    t = np.linspace(0, interval.duration, interval.nsamples)
    return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1


def gen_chirp_wave(freq0: float, freq1: float, interval: Interval) -> np.ndarray:
    t = np.linspace(0, interval.duration, interval.nsamples)
    return chirp(t, f0=freq0, f1=freq1, t1=interval.duration, method="linear")


def gen_white_noise(interval: Interval) -> np.ndarray:
    return np.random.uniform(-1, 1, int(SR * interval.duration))


def write_wav(filename: str, data: np.ndarray):
    write(filename, SR, data)
