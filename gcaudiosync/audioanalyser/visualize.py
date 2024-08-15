from tkinter import font
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
        cbar = fig.colorbar(img,orientation="horizontal")
        cbar.set_label(cmap_label, size=12)
        ax.set_xlabel("Zeit in s",fontsize=12)
        ax.set_ylabel("Frequenz in Hz",fontsize=12)
