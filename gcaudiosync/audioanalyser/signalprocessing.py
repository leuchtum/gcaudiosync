import librosa
import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.setting import Setting


class ProcessedRecording:
    def __init__(self, rr: RawRecording, setting: Setting | None = None) -> None:
        if setting is None:
            setting = Setting.default()
        self._setting = setting
        self.D = librosa.stft(
            rr.data,
            n_fft=setting.n_fft,
            hop_length=setting.hop_length,
            win_length=setting.win_length,
        )
        self.S, self.P = librosa.magphase(self.D)

    @property
    def dS(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_dS"):
            X = self.S
            self._dS = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS

    @property
    def S_db(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_S_db"):
            self._S_db = librosa.amplitude_to_db(self.S, ref=np.max)
        return self._S_db

    @property
    def dS_db(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_dS_db"):
            X = self.S_db
            self._dS_db = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS_db

    @property
    def A(self) -> npt.NDArray[np.float32]:
        if not hasattr(self, "_A"):
            self._A = np.angle(self.P)
        return self._A
