from pathlib import Path
import sys

import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from gcaudiosync.audioanalyser.constants import Constants

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import LazyProcessedRecording
from gcaudiosync.audioanalyser.slicer import SlicerFactory, ValueSlicerConfig
from gcaudiosync.audioanalyser.visualize import plot_spec


def debugger_is_active():
    """Return if the debugger is currently active"""
    return hasattr(sys, "gettrace") and sys.gettrace() is not None


def parse_args():
    """
    Parse command line arguments and return a dictionary with the parsed values.
    Returns:
        dict: A dictionary containing the parsed values.
    Raises:
        ValueError: If the number of arguments is not equal to 6.
    Example usage:
        Cut at 800 Hz
        Slope of -60 Hz/s
        Plotting 10 stripes
        Load file sound/VID_20240103_125230.wav
        Save to output.png
    Results in:
        python plot_spectogram_with_slope.py 800 -60 10 sound/VID_20240103_125230.wav output.png
    """

    if debugger_is_active():
        file = Path("sound/VID_20240103_125230.wav")
        return {
            "hz_bound": 800,
            "slope": 60,
            "stripes": 10,
            "in_file": file,
            "out_file": "out.png",
        }
    if len(sys.argv) != 6:
        msgs = [
            "Invalid number of arguments. Expected 4 arguments.",
            "",
            "Example usage:",
            "\t Cut at 800 Hz",
            "\t Slope of -60 Hz/s",
            "\t Plotting 10 stripes",
            "\t Load file sound/VID_20240103_125230.wav",
            "\t Save to output.png",
            "",
            "Results in:",
            "\tpython plot_spectogram_with_slope.py 800 -60 10 sound/VID_20240103_125230.wav output.png",
        ]
        raise ValueError("\n".join(msgs))
    return {
        "hz_bound": float(sys.argv[1]),
        "slope": float(sys.argv[2]),
        "stripes": int(sys.argv[3]),
        "in_file": Path(sys.argv[4]),
        "out_file": Path(sys.argv[5]),
    }


def load_in_file():
    parsed = parse_args()
    return parsed["in_file"]


def load_out_file():
    parsed = parse_args()
    return parsed["out_file"]


def load_hz_bound():
    parsed = parse_args()
    return parsed["hz_bound"]


def load_slope():
    parsed = parse_args()
    return parsed["slope"]


def load_stripes():
    parsed = parse_args()
    return parsed["stripes"]


def main():
    """
    Main function for plotting a spectrogram with slope.

    This function loads a raw recording from a file, processes it, and plots a spectrogram with a slope.
    The spectrogram is normalized and plotted using matplotlib.
    The slope is calculated based on user-defined parameters.
    The resulting plot is saved as a PNG file.

    Parameters:
    None

    Returns:
    None
    """
    # Rest of the code...
    print("Loading file...")
    rr = RawRecording.from_file(load_in_file())

    consts = Constants(rr.samplerate, rr.data)

    pr = LazyProcessedRecording(
        rr.data,
        n_fft=consts.n_fft,
        hop_length=consts.hop_length,
        win_length=consts.win_length,
    )

    slicer_fac = SlicerFactory(
        n_x=consts.n_time,
        n_y=consts.n_freq,
        x_max=consts.t_max,
        y_max=consts.f_max,
        global_slice_cfg=ValueSlicerConfig(
            from_y=0,
            to_y=load_hz_bound(),
        ),
    )

    slicer = slicer_fac.build()

    S = pr.S_db()[slicer.matrix_slice]
    scaler = MinMaxScaler()
    scaler.fit(S)
    S = scaler.transform(S)

    print("Plotting...")
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_spec(
        S,
        consts.freqs[slicer.from_y],
        consts.time[slicer.from_x],
        consts.t_delta,
        consts.f_delta,
        ax,
        cmap_label="Auf Maximum normierte Amplitude",
        cmap="viridis",
    )

    points = np.linspace(0, consts.t_max, load_stripes() + 1)

    y_start = 0 if load_slope() >= 0 else load_hz_bound()
    y_end = load_hz_bound() if load_slope() >= 0 else 0

    for x_start in points:
        x_end = x_start + (y_end - y_start) / load_slope()
        ax.plot([x_start, x_end], [y_start, y_end], color="white", linewidth=0.5)

    plt.xlim(0, consts.t_max)
    plt.ylim(0, load_hz_bound())
    plt.tight_layout()
    fig.savefig(load_out_file(), format="png", dpi=600)


if __name__ == "__main__":
    """Entery point for the script."""
    main()
