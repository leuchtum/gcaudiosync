from typing import Any, Literal

import matplotlib
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib import animation
from sklearn.preprocessing import MinMaxScaler

from gcaudiosync.audioanalyser.constants import Constants
from gcaudiosync.audioanalyser.slicer import SlicerFactory, ValueSlicerConfig
from gcaudiosync.audioanalyser.util import convert_to_idx


def add_footnote(
    ax: matplotlib.axes.Axes, text: str, loc: Literal["left", "right"] = "right"
) -> matplotlib.axes.Axes:
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
    ax: matplotlib.axes.Axes,
    add_labels: bool = True,
    cmap_label: str = "Amplitude in dB",
    cmap: str = "binary",
    title: str | None = None,
) -> None:
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
    def __init__(
        self,
        *,
        X: npt.NDArray[Any],
        consts: Constants,
        ax: matplotlib.axes.Axes,
        global_slice_cfg: ValueSlicerConfig,
        width: int = 10,
        fps: int = 26,
    ) -> None:
        # Save params
        self.fps = fps
        self.width = width
        self.gloabl_slice_cfg = global_slice_cfg

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

        scaler = MinMaxScaler()
        scaler.fit(X[slicer.matrix_slice])

        X = scaler.transform(X)
        zeros = np.zeros((X.shape[0], self.padding), dtype=X.dtype)
        self.padded_X = np.concatenate([zeros, X, zeros], axis=1)

        extent = (
            -self.width / 2 - 0.5 * consts.t_delta,
            self.width / 2 - 0.5 * consts.t_delta,
            global_slice_cfg.from_y - 0.5 * consts.f_delta,
            global_slice_cfg.to_y - 0.5 * consts.f_delta,
        )

        self.img = ax.imshow(
            self.prepare_matrix(0),
            aspect="auto",
            origin="lower",
            extent=extent,
        )
        ax.vlines(0, global_slice_cfg.from_y, global_slice_cfg.to_y, color="red")
        ax.set_ylim(global_slice_cfg.from_y, global_slice_cfg.to_y)
        ax.set_xlim(-self.width / 2, self.width / 2)
        ax.set_xlabel("Zeitliche Differenz zu t0 in s")
        ax.set_ylabel("Frequenz in Hz")

        fig = ax.get_figure()
        cbar = fig.colorbar(self.img, orientation="horizontal")
        cbar.set_label("Amplitude normiert auf Maximum")

    def prepare_matrix(self, i: int):
        slicer = self.padded_slicer_fac.build(
            ValueSlicerConfig(from_x=i, to_x=i + self.width)
        )
        return self.padded_X[slicer.matrix_slice]

    def callback(self, i: int):
        self.img.set_data(self.prepare_matrix(i))
        return self.img

    def run(self):
        frames = np.linspace(0, self.total_time, self.nof_frames)
        time_diff_in_millis = 1000 / self.fps
        animation.FuncAnimation(
            self.img.get_figure(),
            self.callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        plt.show()
