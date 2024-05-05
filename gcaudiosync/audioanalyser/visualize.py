from typing import Literal

import librosa
import matplotlib
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.setting import Setting


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
    samplerate: float,
    is_db: bool = False,
    footnote: bool = True,
    setting: Setting | None = None,
    ax: matplotlib.axes.Axes | None = None,
    y_axis: Literal["linear", "log"] = "linear",
) -> matplotlib.axes.Axes:
    if setting is None:
        setting = Setting.default()
    if ax is None:
        _, ax = plt.subplots()
    img = librosa.display.specshow(
        X,
        sr=samplerate,
        n_fft=setting.n_fft,
        hop_length=setting.hop_length,
        win_length=setting.win_length,
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
            f"sr={samplerate}\n"
            f"n_fft={setting.n_fft}\n"
            f"hop_length={setting.hop_length}\n"
            f"win_length={setting.win_length}"
        )
        ax = add_footnote(ax, msg)
    return ax
