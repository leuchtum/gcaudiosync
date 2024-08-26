from dataclasses import dataclass
from typing import TypeVar

import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.slicer import Slicer
from gcaudiosync.audioanalyser.util import convert_to_idx

_E = TypeVar("_E", bound=np.generic, covariant=True)


@dataclass(frozen=True)
class _TimeShifter:
    """Class used to shift a signal in time, both back and forth."""

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
class MaskFactory:
    """
    A class that builds binary masks for audio analysis.
    """

    n_time: int
    n_freq: int
    freq_max: float
    time_max: float
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
        self, signal: npt.NDArray[np.float64], slicer: Slicer
    ) -> npt.NDArray[np.bool_]:
        """
        Builds a binary mask based on the given signal and slicer.
        Args:
            signal (npt.NDArray[np.float64]): The input signal.
            slicer (Slicer): The slicer object used to slice the signal.
        Returns:
            npt.NDArray[np.bool_]: The binary mask.
        Raises:
            ValueError: If the signal length does not match the slicer or the
            time axis.
        """
        # Slice the signal first to reduce workload
        if signal.shape[0] == self.n_time:
            sliced_signal = slicer(x=signal)
        elif signal.shape[0] == (slicer.to_x - slicer.from_x):
            sliced_signal = signal
        else:
            msg = "The signal must have the same length as the slicer or the time axis."
            raise ValueError(msg)

        # First, we upsample the signal. With this the grid will get filled better.
        upsample_signal = self._upsample(sliced_signal)

        # original signal as index
        signal_idx = convert_to_idx(
            upsample_signal,
            self.freq_max,
            self.n_freq,
        )

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
        # 5. up only
        # 6. down only
        # 7. right only
        # 8. left only
        # This is an good approximation of the envelope of the signal. Also it's
        # possible to specify the value for the shift for each dim (time and freq).
        buf = np.vstack(
            [
                shifter.pos(signal_idx_plus),
                shifter.neg(signal_idx_plus),
                shifter.pos(signal_idx_minus),
                shifter.neg(signal_idx_minus),
                signal_idx_plus,
                signal_idx_minus,
                shifter.pos(signal_idx),
                shifter.neg(signal_idx),
            ]
        )

        # Get the lower and upper bound
        upsample_lower: npt.NDArray[np.int64] = buf.min(axis=0)
        upsample_upper: npt.NDArray[np.int64] = buf.max(axis=0)

        # Down sample
        lower = upsample_lower[:: self.upsample_factor]
        upper = upsample_upper[:: self.upsample_factor]

        # Broadcast magic...
        rows = np.arange(slicer.from_y, slicer.to_y, dtype=np.int64)
        above = rows >= lower[:, None]
        below = rows <= upper[:, None]
        return (above & below).T
