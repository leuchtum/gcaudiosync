from typing import Any, Literal

import librosa
import matplotlib
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.constants import Constants


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


def spectrogram(
    X: npt.NDArray[np.float32],
    constants: Constants,
    is_db: bool = False,
    footnote: bool = True,
    ax: matplotlib.axes.Axes | None = None,
    y_axis: Literal["linear", "log"] = "linear",
) -> matplotlib.axes.Axes:
    # Raise, since this function is really outdated
    raise NotImplementedError
    if ax is None:
        _, ax = plt.subplots()
    img = librosa.display.specshow(
        X,
        sr=constants.sr,
        n_fft=constants.n_fft,
        hop_length=constants.hop_length,
        win_length=constants.win_length,
        x_axis="time",
        y_axis=y_axis,
        ax=ax,
    )
    if is_db:
        plt.colorbar(img, ax=ax, format="%+2.0f dB")
    else:
        plt.colorbar(img, ax=ax)
    if footnote:
        msg = (
            f"is_db: {is_db}\n"
            f"sr={constants.sr}\n"
            f"n_fft={constants.n_fft}\n"
            f"hop_length={constants.hop_length}\n"
            f"win_length={constants.win_length}"
        )
        ax = add_footnote(ax, msg)
    return ax


def plot_spec(
    X: npt.NDArray[Any],
    freq_min: float,
    time_min: float,
    time_delta: float,
    freq_delta: float,
    ax: matplotlib.axes.Axes,
    add_labels: bool = True,
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
            cmap="binary",
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
        fig.colorbar(
            img,
            orientation="horizontal",
            label="Magnitude [dB]",
        )
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Frequency [Hz]")
