from dataclasses import dataclass
from typing import Self


@dataclass
class Setting:
    n_fft: int
    hop_length: int
    win_length: int

    @classmethod
    def default(cls) -> Self:
        # Defaults are chosen based on the default values of librosa.stft but
        # not exactly the same.
        # https://librosa.org/doc/latest/generated/librosa.stft.html#librosa.stft
        n_fft = 2**14
        win_length = 2**13
        hop_length = 2**9
        return cls(n_fft=n_fft, hop_length=hop_length, win_length=win_length)
