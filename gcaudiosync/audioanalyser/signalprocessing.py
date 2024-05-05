from dataclasses import dataclass
from typing import Self

import librosa
import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.setting import Setting


@dataclass
class ProcessedRecording:
    samplerate: float
    D: npt.NDArray[np.complex64]  # STFT
    S: npt.NDArray[np.float32]  # Magnitude
    S_db: npt.NDArray[np.float32]  # Magnitude in dB
    P: npt.NDArray[np.complex64]  # Phase
    A: npt.NDArray[np.float32]  # Angle of phase in radians

    @classmethod
    def from_raw(cls, rr: RawRecording, setting: Setting | None = None) -> Self:
        if setting is None:
            setting = Setting.default()
        D = librosa.stft(
            rr.data,
            n_fft=setting.n_fft,
            hop_length=setting.hop_length,
            win_length=setting.win_length,
        )
        S, P = librosa.magphase(D)
        S_db = librosa.amplitude_to_db(S, ref=np.max)
        A = np.angle(P)
        return cls(samplerate=rr.samplerate, D=D, S=S, S_db=S_db, P=P, A=A)
