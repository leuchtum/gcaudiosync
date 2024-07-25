import librosa
import numpy as np
import numpy.typing as npt

N_FFT = 2**14
WIN_LENGTH = 2**13
HOP_LENGTH = 2**9


class Constants:
    def __init__(self, data: npt.NDArray[np.float32], sr: int) -> None:
        self.n_fft = N_FFT
        self.win_length = WIN_LENGTH
        self.hop_length = HOP_LENGTH
        self.sr = sr
        self.freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
        self.time = librosa.times_like(data, sr=sr)

    @property
    def t_max(self) -> float:
        return self.time[-1]  # type: ignore

    @property
    def f_max(self) -> float:
        return self.freqs[-1]  # type: ignore

    @property
    def t_delta(self) -> float:
        return self.time[1] - self.time[0]  # type: ignore

    @property
    def f_delta(self) -> float:
        return self.freqs[1] - self.freqs[0]  # type: ignore

    @property
    def n_time(self) -> int:
        return len(self.time)

    @property
    def n_freq(self) -> int:
        return len(self.freqs)
