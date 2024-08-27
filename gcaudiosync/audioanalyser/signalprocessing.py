import librosa
import numpy as np
import numpy.typing as npt


class ProcessedRecording:
    """Class for processing audio data."""

    def __init__(
        self,
        data: npt.NDArray[np.float32],
        *,
        n_fft: int,
        hop_length: int,
        win_length: int,
    ) -> None:
        # The main workload of this class is the Short-Time Fourier Transform,
        # this will only be done once.
        self._D = librosa.stft(
            data,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=win_length,
        )

    def D(self) -> npt.NDArray[np.complex64]:
        """Get the complex Short-Time Fourier Transform."""
        return self._D

    def _build_S_and_P(self) -> None:
        self._S, self._P = librosa.magphase(self.D())

    def S(self) -> npt.NDArray[np.float32]:
        """Get the magnitude of the Short-Time Fourier Transform."""
        if not hasattr(self, "_S"):
            self._build_S_and_P()
        return self._S

    def S_sqrt(self) -> npt.NDArray[np.float32]:
        """Get the square root of the magnitude of the Short-Time Fourier Transform."""
        if not hasattr(self, "_S_sqrt"):
            self._S_sqrt = np.sqrt(self.S())
        return self._S_sqrt

    def P(self) -> npt.NDArray[np.complex64]:
        """Get the phase of the Short-Time Fourier Transform."""
        if not hasattr(self, "_P"):
            self._build_S_and_P()
        return self._P

    def dS(self) -> npt.NDArray[np.float32]:
        """Get the derivative of the magnitude of the Short-Time Fourier Transform."""
        if not hasattr(self, "_dS"):
            X = self.S()
            self._dS = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS

    def S_db(self) -> npt.NDArray[np.float32]:
        """Get the magnitude of the Short-Time Fourier Transform in decibels."""
        if not hasattr(self, "_S_db"):
            self._S_db = librosa.amplitude_to_db(self.S(), ref=np.max)
        return self._S_db

    def dS_db(self) -> npt.NDArray[np.float32]:
        """Get the derivative of the magnitude of the Short-Time Fourier Transform in decibels."""
        if not hasattr(self, "_dS_db"):
            X = self.S_db()
            self._dS_db = np.diff(X, axis=1, append=X[:, [-1]])
        return self._dS_db

    def A(self) -> npt.NDArray[np.float32]:
        """Get the angle of the Short-Time Fourier Transform."""
        if not hasattr(self, "_A"):
            self._A = np.angle(self.P())
        return self._A
