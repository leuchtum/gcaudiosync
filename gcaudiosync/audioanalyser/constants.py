import librosa
import numpy as np
import numpy.typing as npt

N_FFT = 2**14
WIN_LENGTH = 2**13
HOP_LENGTH = 2**9


class Constants:
    """Class that holds the constants that are relevant throughout the analysis."""

    def __init__(self, sr: float, data: npt.NDArray[np.float32]) -> None:
        """
        Initialize the AudioAnalyser object.

        Parameters:
        - sr (float): The sample rate of the audio data.
        - data (npt.NDArray[np.float32]): The audio data.

        Returns:
        - None
        """

        self.n_fft = N_FFT
        self.win_length = WIN_LENGTH
        self.hop_length = HOP_LENGTH
        self.sr = sr
        self.freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)

        n_frames = data.shape[0] // self.hop_length + 1
        self.time = librosa.times_like(n_frames, sr=sr)

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
