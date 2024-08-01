from dataclasses import dataclass
from typing import TypeVar

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

from gcaudiosync.audioanalyser.slicer import Slicer, SlicerFactory, ValueSlicerConfig
from gcaudiosync.audioanalyser.util import convert_to_idx
from gcaudiosync.audioanalyser.visualize import plot_spec

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


def sandbox() -> None:
    x_max = 20
    n_x = 2000

    y_max = 15000
    n_y = 2000

    slicer_fac = SlicerFactory(
        n_x=n_x,
        n_y=n_y,
        x_max=x_max,
        y_max=y_max,
        global_slice_cfg=ValueSlicerConfig(from_y=5000, to_y=11000),
    )

    slicer = slicer_fac.build(ValueSlicerConfig(from_x=1, to_x=4))

    x = np.linspace(0, x_max, n_x, endpoint=False)
    y = 1000 * abs(x - x.mean()) + 500
    y[200:300] = 1000

    mask_fac = MaskFactory(
        n_time=n_x,
        n_freq=n_y,
        freq_max=y_max,
        time_max=x_max,
        time_window=0.5,
        freq_window=100,
    )

    image = -1 * np.ones((n_y, n_x), dtype=np.float64)
    mask = mask_fac.build_binary_mask(y, slicer).astype(np.float64)
    image[slicer.matrix_slice] = mask

    _, ax = plt.subplots()
    plot_spec(image, 0, 0, x_max / n_x, y_max / n_y, ax)
    plt.plot(x, y, color="red")
    plt.show()


if __name__ == "__main__":
    sandbox()
