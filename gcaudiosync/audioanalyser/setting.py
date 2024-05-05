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
        n_fft = 512
        win_length = n_fft // 2  # librosa defaults to win_length=n_fft
        hop_length = win_length // 4
        return cls(n_fft=n_fft, hop_length=hop_length, win_length=win_length)
