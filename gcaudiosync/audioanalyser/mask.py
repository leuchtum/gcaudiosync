from dataclasses import dataclass
from typing import TypeVar

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

from gcaudiosync.audioanalyser.util import convert_to_idx

_E = TypeVar("_E", bound=np.generic, covariant=True)


@dataclass(frozen=True)
class _TimeShifter:
    shift: int

    def neg(self, x: npt.NDArray[_E]) -> npt.NDArray[_E]:
        # Helper function to shift a signal to the left (back in time). The
        # missing values on the right will get filled with the most right
        # value of the signal.
        p = np.roll(x, -self.shift)
        p[-self.shift :] = x[-1]
        return p

    def pos(self, x: npt.NDArray[_E]) -> npt.NDArray[_E]:
        # Helper function to shift a signal to the right.
        p = np.roll(x, self.shift)
        p[: self.shift] = x[0]
        return p


@dataclass(kw_only=True, frozen=True)
class MaskBuilder:
    """
    A class that builds binary and blurred masks for audio analysis.
    """

    n_time: int
    n_freq: int
    freq_max: float
    time_max: float
    upper_cut_freq: float
    lower_cut_freq: float
    time_window: float
    freq_window: float
    upsample_factor: int = 10

    def _upsample(self, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        n_samples = len(x) * self.upsample_factor
        return np.interp(
            np.linspace(0, len(x) - 1, n_samples, endpoint=False),
            np.arange(len(x)),
            x,
        )

    def build_binary_mask(
        self, signal: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.bool_]:
        # First, we upsample the signal. With this the grid will get filled better.
        upsample_signal = self._upsample(signal)

        # Now we shift the signal up and down
        signal_idx_plus = convert_to_idx(
            upsample_signal + self.freq_window / 2,
            self.freq_max,
            self.n_freq,
        )
        signal_idx_minus = convert_to_idx(
            upsample_signal - self.freq_window / 2,
            self.freq_max,
            self.n_freq,
        )

        # Now we determine the time shift factor.
        time_shift = convert_to_idx(
            self.time_window / 2,
            self.time_max,
            self.n_time,
        )
        time_shift *= self.upsample_factor
        shifter = _TimeShifter(time_shift)

        # This buffer is the main idea of this method. We shift the signal
        # 1. up and right
        # 2. up and left
        # 3. down and right
        # 4. down and left
        # This is an good approximation of the envelope of the signal. Also it's
        # possible to specify the value for the shift for each dim (time and freq).
        buf = np.vstack(
            [
                shifter.pos(signal_idx_plus),
                shifter.neg(signal_idx_plus),
                shifter.pos(signal_idx_minus),
                shifter.neg(signal_idx_minus),
            ]
        )

        # Get the lower and upper bound
        upsample_lower: npt.NDArray[np.int64] = buf.min(axis=0)
        upsample_upper: npt.NDArray[np.int64] = buf.max(axis=0)

        # Down sample
        lower = upsample_lower[:: self.upsample_factor]
        upper = upsample_upper[:: self.upsample_factor]

        # Broadcast magic...
        rows = np.arange(self.lower_cut_idx, self.upper_cut_idx, dtype=np.int64)
        above = rows >= lower[:, None]
        below = rows <= upper[:, None]
        return (above & below).T

    @property
    def lower_cut_idx(self) -> int:
        return convert_to_idx(self.lower_cut_freq, self.freq_max, self.n_freq)

    @property
    def upper_cut_idx(self) -> int:
        return convert_to_idx(self.upper_cut_freq, self.freq_max, self.n_freq)


def sandbox() -> None:
    T_max = 20
    T_samples = 2000

    F_max = 15000
    F_samples = 2000

    time = np.linspace(0, T_max, T_samples, endpoint=False)
    signal = 1500 * abs(time - time.mean())
    signal = 10000 * np.ones_like(time)
    signal[500:1500] = 0

    fb = MaskBuilder(
        n_time=T_samples,
        n_freq=F_samples,
        freq_max=F_max,
        time_max=T_max,
        time_window=0.5,
        freq_window=100,
        upper_cut_freq=15000,
        lower_cut_freq=20,
    )

    W = fb.build_binary_mask(signal).astype(np.float64)

    plt.imshow(
        W,
        aspect="auto",
        origin="lower",
        extent=(0, T_max, fb.lower_cut_freq, fb.upper_cut_freq),
    )
    plt.plot(time, signal, color="red")
    plt.show()


if __name__ == "__main__":
    sandbox()
