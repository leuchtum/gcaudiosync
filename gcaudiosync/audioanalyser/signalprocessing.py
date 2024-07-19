import re
from random import sample
from typing import Literal, Protocol

import librosa
import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.setting import Setting


class GenericProcessedRecording(Protocol):
    setting: Setting
    samplerate: float

    def D(self) -> npt.NDArray[np.complex64]: ...
    def P(self) -> npt.NDArray[np.complex64]: ...
    def S(self) -> npt.NDArray[np.float32]: ...
    def dS(self) -> npt.NDArray[np.float32]: ...
    def S_db(self) -> npt.NDArray[np.float32]: ...
    def dS_db(self) -> npt.NDArray[np.float32]: ...
    def A(self) -> npt.NDArray[np.float32]: ...


class LazyProcessedRecording(GenericProcessedRecording):
    def __init__(
        self,
        data: npt.NDArray[np.float32],
        samplerate: float,
        setting: Setting | None = None,
    ) -> None:
        if setting is None:
            setting = Setting.default()
        self.setting = setting

        self.samplerate = samplerate

        self._D = librosa.stft(
            data,
            n_fft=setting.n_fft,
            hop_length=setting.hop_length,
            win_length=setting.win_length,
        )

    def D(self) -> npt.NDArray[np.complex64]:
        return self._D

    def _build_S_and_P(self) -> None:
        self._S, self._P = librosa.magphase(self.D())

    def S(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_S"):
            self._build_S_and_P()
        return self._S

    def P(self) -> npt.NDArray[np.complex64]:
        if not hasattr(self, "_P"):
            self._build_S_and_P()
        return self._P

    def dS(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_dS"):
            X = self.S()
            self._dS = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS

    def S_db(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_S_db"):
            self._S_db = librosa.amplitude_to_db(self.S(), ref=np.max)
        return self._S_db

    def dS_db(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_dS_db"):
            X = self.S_db()
            self._dS_db = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS_db

    def A(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_A"):
            self._A = np.angle(self.P())
        return self._A
