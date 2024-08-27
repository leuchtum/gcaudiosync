"""This file contains a script that plots a spectrogram with a given slope."""

from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from gcaudiosync.audioanalyser.constants import Constants
from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import ProcessedRecording
from gcaudiosync.audioanalyser.slicer import SlicerFactory, ValueSlicerConfig
from gcaudiosync.audioanalyser.visualize import plot_spec


def main(
    audio_file: Path,
    out_directory: Path,
    slope: float,
    n_stripes: int,
    hz_bound: float,
) -> None:
    # Loading the file
    print("Loading file...")
    rr = RawRecording(audio_file)

    # Initializing the constants
    consts = Constants(rr.samplerate, rr.data)

    # Processing the recording
    pr = ProcessedRecording(
        rr.data,
        n_fft=consts.n_fft,
        hop_length=consts.hop_length,
        win_length=consts.win_length,
    )

    # Get a slicer factory object. This will factory will be invoked to create a
    # slicer object. The slicer object will be used to slice the spectrogram
    # matrix. Here we slice the frequency in the interval [0, hz_bound].
    slicer_fac = SlicerFactory(
        n_x=consts.n_time,
        n_y=consts.n_freq,
        x_max=consts.t_max,
        y_max=consts.f_max,
        global_slice_cfg=ValueSlicerConfig(
            from_y=0,
            to_y=hz_bound,
        ),
    )

    # Create a slicer object
    slicer = slicer_fac.build()

    # Get the sliced spectrogram matrix and normalize it
    S = pr.S_db()[slicer.matrix_slice]
    scaler = MinMaxScaler()
    scaler.fit(S)
    S = scaler.transform(S)

    # Plot the spectrogram
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

    # Helper arrays for the slope
    points = np.linspace(0, consts.t_max, n_stripes)
    y_start = 0 if slope >= 0 else hz_bound
    y_end = hz_bound if slope >= 0 else 0

    # Plot the slopes
    for x_start in points:
        x_end = x_start + (y_end - y_start) / slope
        ax.plot([x_start, x_end], [y_start, y_end], color="white", linewidth=0.5)

    # Save the plot
    plt.xlim(0, consts.t_max)
    plt.ylim(0, hz_bound)
    if n_stripes > 0:
        plt.title(f"Spektrogramm mit Steigung {slope} Hz/s")
    plt.tight_layout()
    fig.savefig(out_directory / "spectrogram_with_slope.png", format="png", dpi=600)


if __name__ == "__main__":
    main(
        audio_file=Path("sound") / "VID_20240103_125230.wav",
        out_directory=Path("output"),
        slope=60,
        n_stripes=100,
        hz_bound=1000,
    )
