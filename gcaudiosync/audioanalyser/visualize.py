from typing import Any, Literal

from matplotlib.artist import Artist
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.animation import FuncAnimation
from sklearn.preprocessing import MinMaxScaler

from gcaudiosync.audioanalyser.constants import Constants
from gcaudiosync.audioanalyser.slicer import SlicerFactory, ValueSlicerConfig
from gcaudiosync.audioanalyser.util import convert_to_idx


def add_footnote(ax: Axes, text: str, loc: Literal["left", "right"] = "right") -> Axes:
    """Helper function to add a footnote to a plot."""
    if loc == "left":
        xy = (0.0, -0.15)
        ha = "left"
    else:
        xy = (1.0, -0.15)
        ha = "right"
    ax.annotate(text, xy=xy, ha=ha, xycoords="axes fraction", va="top")
    return ax


def plot_spec(
    X: npt.NDArray[Any],
    freq_min: float,
    time_min: float,
    time_delta: float,
    freq_delta: float,
    ax: Axes,
    add_labels: bool = True,
    cmap_label: str = "Amplitude in dB",
    cmap: str = "binary",
    title: str | None = None,
) -> None:
    """Plot the spectrogram."""
    extent = (
        time_min - 0.5 * time_delta,
        time_min + (X.shape[1] - 0.5) * time_delta,
        freq_min - 0.5 * freq_delta,
        freq_min + (X.shape[0] - 0.5) * freq_delta,
    )
    if X.ndim == 2:
        img = ax.imshow(
            X,
            aspect="auto",
            origin="lower",
            extent=extent,
            cmap=cmap,
        )
    else:
        img = ax.imshow(
            X,
            aspect="auto",
            origin="lower",
            extent=extent,
        )
    if add_labels:
        fig = ax.get_figure()
        if fig is None:
            raise ValueError("Fig not found")
        cbar = fig.colorbar(img, orientation="horizontal")
        cbar.set_label(cmap_label, size=12)
        ax.set_xlabel("Zeit in s", fontsize=12)
        ax.set_ylabel("Frequenz in Hz", fontsize=12)
    if title is not None:
        ax.set_title(title)


class SpectroAnimator:
    """Class to animate a spectrogram."""

    def __init__(
        self,
        *,
        X: npt.NDArray[np.float64] | npt.NDArray[np.float32],
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        consts: Constants,
        ax: Axes,
        global_slice_cfg: ValueSlicerConfig,
        width: int = 10,
        fps: int = 26,
    ) -> None:
        # Save params
        self.fps = fps
        self.width = width
        self.gloabl_slice_cfg = global_slice_cfg
        self.x = x
        self.y = y

        self.frame_delta_time: float = 1 / self.fps
        self.total_time = consts.t_max
        self.nof_frames = int(self.total_time / self.frame_delta_time)

        # Reduce matrix
        self.padding = convert_to_idx(self.width / 2, consts.t_max, consts.n_time)
        self.padded_slicer_fac = SlicerFactory(
            n_x=consts.n_time + 2 * self.padding,
            n_y=consts.n_freq,
            x_max=consts.t_max + self.width,
            y_max=consts.f_max,
            global_slice_cfg=global_slice_cfg,
        )
        self.slicer_fac = SlicerFactory(
            n_x=consts.n_time,
            n_y=consts.n_freq,
            x_max=consts.t_max,
            y_max=consts.f_max,
            global_slice_cfg=global_slice_cfg,
        )
        slicer = self.slicer_fac.build()

        # Transform and pad matrix
        scaler = MinMaxScaler()
        scaler.fit(X[slicer.matrix_slice])

        X = scaler.transform(X)
        zeros = np.zeros((X.shape[0], self.padding), dtype=X.dtype)
        self.padded_X = np.concatenate([zeros, X, zeros], axis=1)

        from_y = 0 if global_slice_cfg.from_y is None else global_slice_cfg.from_y
        to_y = consts.f_max if global_slice_cfg.to_y is None else global_slice_cfg.to_y

        extent = (
            -self.width / 2 - 0.5 * consts.t_delta,
            self.width / 2 - 0.5 * consts.t_delta,
            from_y - 0.5 * consts.f_delta,
            to_y - 0.5 * consts.f_delta,
        )

        # Plot spec
        self.img = ax.imshow(
            self.prepare_matrix(0),
            aspect="auto",
            origin="lower",
            extent=extent,
        )

        # Plot target freq line
        (self.target_freq_line,) = ax.plot(
            [extent[0], 0, extent[1]],
            [self.y[0], self.y[0], self.y[0]],
            color="red",
            linestyle="dashed",
            marker="o",
            markersize=4,
        )

        # Plot red center line
        ax.vlines(0, from_y, to_y, color="red")

        # Add labels and make it pretty
        ax.set_ylim(from_y, to_y)
        ax.set_xlim(-self.width / 2, self.width / 2)
        ax.set_xlabel("Zeitliche Differenz zu t0 in s")
        ax.set_ylabel("Frequenz in Hz")

        # Add colorbar
        fig = ax.get_figure()
        if fig is None:
            raise ValueError("Fig not found")
        cbar = fig.colorbar(self.img, orientation="horizontal")
        cbar.set_label("Amplitude normiert auf Maximum")

    def prepare_matrix(self, frame_s: float) -> npt.NDArray[np.float64]:
        slicer = self.padded_slicer_fac.build(
            ValueSlicerConfig(from_x=frame_s, to_x=frame_s + self.width)
        )
        return self.padded_X[slicer.matrix_slice]  # type: ignore

    def callback(self, frame_s: float) -> list[Artist]:
        idx = np.argmin((frame_s - self.x) >= 0) - 1
        self.target_freq_line.set_ydata([self.y[idx], self.y[idx], self.y[idx]])
        self.img.set_data(self.prepare_matrix(frame_s))
        return [self.target_freq_line, self.img]

    def run(self) -> None:
        frames = np.linspace(0, self.total_time, self.nof_frames)
        time_diff_in_millis = 1000 / self.fps
        fig = self.img.get_figure()
        if fig is None:
            raise ValueError("Fig not found")
        FuncAnimation(
            fig,
            self.callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        plt.show()
