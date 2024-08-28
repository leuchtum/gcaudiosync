"""This file contains the core functionality of the gcaudiosync package."""

from pathlib import Path
from typing import Any

import matplotlib.axes
import numpy as np
import numpy.typing as npt
import pandas as pd
import tqdm
from matplotlib import pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.artist import Artist

from gcaudiosync.audioanalyser.constants import Constants
from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.mask import MaskFactory
from gcaudiosync.audioanalyser.optimize import RefPointOptimizer
from gcaudiosync.audioanalyser.piecewise import (
    BendedSegmentBuilder,
    ParametrisableFormFunc,
)
from gcaudiosync.audioanalyser.signalprocessing import ProcessedRecording
from gcaudiosync.audioanalyser.slicer import (
    IndexSlicerConfig,
    Slicer,
    SlicerFactory,
    ValueSlicerConfig,
)
from gcaudiosync.audioanalyser.visualize import SpectroAnimator, plot_spec
from gcaudiosync.gcanalyser.alternativetoolpathgenerator import (
    AlternativeToolPathAnimator,
)
from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser
from gcaudiosync.helper import debugger_is_active

PLOT = True


def _plot_base_spec(
    S: npt.NDArray[Any],
    slicer: Slicer,
    consts: Constants,
    ax: matplotlib.axes.Axes,
    title: str | None,
) -> None:
    plot_spec(
        S[slicer.matrix_slice] / S[slicer.matrix_slice].max(),
        consts.freqs[slicer.from_y],
        consts.time[slicer.from_x],
        consts.t_delta,
        consts.f_delta,
        ax,
        cmap_label="Auf Maximum normierte Amplitude",
        cmap="binary",
        title=title,
    )
    if title is not None:
        ax.set_title(title)


def plot_spec_raw(
    matrix: npt.NDArray[Any],
    slicer: Slicer,
    consts: Constants,
    title: str | None = None,
    outfile: Path | None = None,
) -> None:
    # Create a figure and axis to plot to
    fig, ax = plt.subplots(figsize=(8, 5))

    # First, plot the base spectrogram
    _plot_base_spec(matrix, slicer, consts, ax, title)

    # Make it pretty
    fig.tight_layout()

    # Save the figure if an outfile is specified
    if outfile is not None:
        fig.savefig(outfile, dpi=400)

    # Close the figure if the debugger is not active. This is done to prevent
    # large amounts of figures from being opened when running the program,
    # saving memory.
    if not debugger_is_active():
        fig.clear()
        plt.close(fig)


def plot_spec_with_param_func(
    matrix: npt.NDArray[Any],
    slicer: Slicer,
    consts: Constants,
    times: npt.NDArray[Any],
    freqs: npt.NDArray[Any],
    param_form_func: ParametrisableFormFunc,
    title: str | None = None,
    outfile: Path | None = None,
) -> None:
    # Create a figure and axis to plot to
    fig, ax = plt.subplots(figsize=(8, 5))

    # First, plot the base spectrogram
    _plot_base_spec(matrix, slicer, consts, ax, title)

    # Plot the guessed times and frequencies
    param_form_func.set_ref_points(times, freqs)
    y = param_form_func.get_parametrized()(consts.time)
    ax.plot(consts.time, y, "r")

    # Make it pretty
    fig.tight_layout()

    # Save the figure if an outfile is specified
    if outfile is not None:
        fig.savefig(outfile, dpi=400)

    # Close the figure if the debugger is not active. This is done to prevent
    # large amounts of figures from being opened when running the program,
    # saving memory.
    if not debugger_is_active():
        fig.clear()
        plt.close(fig)


def main(
    *,
    gc_file: Path,
    audio_file: Path,
    parameter_file: Path,
    snapshot_file: Path,
    out_directory: Path,
    ramp_up_slope: float,
    ramp_down_slope: float,
    hz_bound: float,
) -> None:
    # Read in the audio file and create all the necessary objects
    print("Reading in audio file...")
    rr = RawRecording(audio_file)
    consts = Constants(rr.samplerate, rr.data)
    pr = ProcessedRecording(
        rr.data,
        n_fft=consts.n_fft,
        hop_length=consts.hop_length,
        win_length=consts.win_length,
    )

    # Create a G_Code_Analyser
    gc_analyser = GCodeAnalyser(
        parameter_src=parameter_file,
        snapshot_src=snapshot_file,
    )

    # Analyse G-Code
    print("Analysing G-Code...")
    gc_analyser.analyse(gc_file)

    # Get the frequency information from the analysed G-Code and convert into a
    # timing and freq array. Also convert guessed times from milliseconds to
    # seconds.
    print("Converting G-Code information...")
    freq_infos = gc_analyser.Sync_Info_Manager.frequency_information
    freqs_guess = np.array(
        [fi.frequency for fi in freq_infos],
        dtype=np.float64,
    )
    times_guess = np.array(
        [fi.expected_time_start for fi in freq_infos],
        dtype=np.float64,
    )
    times_guess /= 1000

    # Check if guessed times are not zero. Otherwise break the program
    if np.all(times_guess == 0):
        raise ValueError("Guessed times are zero, cannot continue")

    # Add a terminal reference point to the guesses
    max_time = max(times_guess[-1] + 1, consts.t_max)
    times_guess = np.concatenate((times_guess, [max_time]))
    freqs_guess = np.concatenate((freqs_guess, [0]))

    # Create parametrisable form function with the slopes specified. When
    # invoking the form function, the guessed times and frequencies will later
    # be used to create a parametrized form function.
    param_form_func = ParametrisableFormFunc(
        BendedSegmentBuilder(
            ramp_up_slope=ramp_up_slope,
            ramp_down_slope=ramp_down_slope,
        )
    )

    # Create the mask factory, which will later be used to create the masks from
    # a parametrized form function.
    mask_fac = MaskFactory(
        n_time=consts.n_time,
        n_freq=consts.n_freq,
        freq_max=consts.f_max,
        time_max=consts.t_max,
        time_window=5 * consts.t_delta,
        freq_window=5 * consts.f_delta,
    )

    # Create the slicer factory, which will later be used to create the slicers.
    smallest_not_zero_freq = freqs_guess[freqs_guess != 0].min()
    first_harmonic_of_max_freq = freqs_guess.max() * 2
    buffer = 15  # Hz; Used to relax the boundaries
    slice_from_freq = min(smallest_not_zero_freq - buffer, 100)
    slice_to_freq = max(first_harmonic_of_max_freq + buffer, 100)
    slicer_fac = SlicerFactory(
        n_x=consts.n_time,
        n_y=consts.n_freq,
        x_max=consts.t_max,
        y_max=consts.f_max,
        global_slice_cfg=ValueSlicerConfig(
            from_y=slice_from_freq,
            to_y=slice_to_freq,
        ),
    )

    # For reference, plot the spectrogram as well as the spectrogram with the
    # guessed times and frequencies. For this a seperate slicer is used, which
    # is only used for plotting.
    slice_to_freq_plot_only = int(
        np.argmax(consts.freqs > np.ceil(slice_to_freq / 1e3) * 1e3)
    )
    slicer_fac_plot_only = SlicerFactory(
        n_x=consts.n_time,
        n_y=consts.n_freq,
        x_max=consts.t_max,
        y_max=consts.f_max,
        global_slice_cfg=IndexSlicerConfig(to_y=slice_to_freq_plot_only),
    )
    if PLOT:
        plot_spec_raw(
            pr.S(),
            slicer_fac_plot_only.build(),
            consts,
            outfile=out_directory / "spectrogram_unprocessed.png",
            title="Spektrogramm; nicht aufbereitet",
        )
        plot_spec_raw(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            outfile=out_directory / "spectrogram_processed.png",
            title="Spektrogramm; aufbereitet",
        )
        plot_spec_with_param_func(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            times_guess,
            freqs_guess,
            param_form_func,
            outfile=out_directory / "spectrogram_with_guesses.png",
            title="Spektrogramm; aufbereitet; mit Schätzungen",
        )

    # Setup the optimization
    rpo = RefPointOptimizer(
        param_form_func=param_form_func,
        x_sample=consts.time,
        mask_factory=mask_fac,
        slicer_factory=slicer_fac,
        S=pr.S_sqrt(),
        dx=consts.t_delta,
        dy=consts.f_delta,
        use_1st_harmonic=True,
    )

    # Pre-optimize the guessed times
    print("Pre-optimizing guessed times...")
    times_guess, freqs_guess = rpo.optimize_all_x(times_guess, freqs_guess, 0.2)

    # Plot the spectrogram with the pre-optimized guesses
    if PLOT:
        print("Plotting and save spectrogram after pre-optimization...")
        plot_spec_with_param_func(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            times_guess,
            freqs_guess,
            param_form_func,
            outfile=out_directory / "spectrogram_with_preoptimized_guesses.png",
            title="Spektrogramm; aufbereitet; mit vor-optimierten Schätzungen",
        )

    # Optimize the guessed frequencies
    print("Optimizing guessed frequencies...")
    for i in range(1, len(freqs_guess) - 1):
        if freqs_guess[i] == 0:
            continue
        times_guess, freqs_guess = rpo.optimize_yi(
            times_guess,
            freqs_guess,
            i,
            freqs_guess[i] - 30,
            freqs_guess[i] + 30,
            1,
        )

    # Optimize the guessed times
    print("Optimizing guessed times...")
    for i in range(1, len(times_guess) - 1):
        diff_to_prev = times_guess[i] - times_guess[i - 1]
        diff_to_next = times_guess[i + 1] - times_guess[i]
        times_guess, freqs_guess = rpo.optimize_xi(
            times_guess,
            freqs_guess,
            i,
            times_guess[i] - diff_to_prev / 2,
            times_guess[i] + diff_to_next / 2,
            1,
        )

    # Plot the spectrogram with the optimized guesses
    if PLOT:
        print("Plotting and save spectrogram after optimization...")
        plot_spec_with_param_func(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            times_guess,
            freqs_guess,
            param_form_func,
            outfile=out_directory / "spectrogram_with_optimized_guesses.png",
            title="Spektrogramm; aufbereitet; mit optimierten Schätzungen",
        )

    # Saving the optimized guesses to csv
    print("Saving optimized guesses to csv...")
    pd.DataFrame(
        {
            "time [s]": times_guess,
            "freq [Hz]": freqs_guess,
        }
    ).to_csv("optimized_guesses.csv", index=False)

    # Inform the GCode Analyser about the optimized times
    print("Informing G-Code Analyser about optimized times...")
    start_time_by_freqs = times_guess[1]
    total_time_by_freqs = times_guess[-2] - start_time_by_freqs

    time_before_first_freq = (
        gc_analyser.Movement_Manager.get_expected_time_of_gcode_line(
            freq_infos[0].g_code_line_index_end
        )
    )
    time_after_last_freq = gc_analyser.Movement_Manager.get_expected_time_of_gcode_line(
        freq_infos[-1].g_code_line_index_start
    )
    gc_analyser.set_start_time_and_total_time(
        start_time_by_freqs * 1000 - time_before_first_freq,
        total_time_by_freqs * 1000 + time_before_first_freq + time_after_last_freq,
    )

    for freq_info, gc_timestamp in zip(freq_infos[:-1], times_guess[:-2]):
        gc_index = freq_info.g_code_line_index_start

        try:
            gc_analyser.adjust_start_time_of_g_code_line(gc_index, 1000 * gc_timestamp)
        except Exception as e:
            g_code = gc_analyser.g_code[gc_index]
            msg = "\n".join(
                [
                    "Warning:",
                    f"Could not adjust start time of GCode '{g_code}' at line {gc_index}.",
                    f"Original error: {e.__class__.__name__}: {e}",
                ]
            )
            print(msg)

    # Plot the tool path. For this we crate an animation, which will be saved as
    # an mp4 file. We animate via two Animator objects, one for the tool path
    # and one for the spectrogram. Then the callback function is used to update
    # each frame.
    if PLOT:
        print("Plotting and saving tool path...")
        fps = 26
        fig = plt.figure(figsize=(15, 5))
        ax_info = fig.add_subplot(1, 7, (1, 2))
        ax_tool = fig.add_subplot(1, 7, (3, 4))
        ax_spec = fig.add_subplot(1, 7, (5, 7))
        toolpath_ani = AlternativeToolPathAnimator(
            gc_analyser.Movement_Manager,
            gc_analyser.g_code,
            ax_tool,
            ax_info,
            consts.t_max,
            fps=fps,
        )
        spec_ani = SpectroAnimator(
            X=pr.S_db(),
            x=times_guess,
            y=freqs_guess,
            consts=consts,
            ax=ax_spec,
            global_slice_cfg=ValueSlicerConfig(
                from_y=0,
                to_y=hz_bound,
            ),
        )
        progressbar = tqdm.tqdm(total=spec_ani.nof_frames)

        def callback(frame_s: float) -> list[Artist]:
            plt_objs: list[Artist] = []
            plt_objs.extend(toolpath_ani.callback(frame_s))
            plt_objs.extend(spec_ani.callback(frame_s))
            progressbar.update(1)
            return plt_objs

        frames = np.linspace(0, spec_ani.total_time, spec_ani.nof_frames)
        time_diff_in_millis = 1000 / fps
        anim = FuncAnimation(
            fig,
            callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        fig.tight_layout()
        writer = FFMpegWriter(fps=fps)
        anim.save(out_directory / "toolpath_with_spectrogram.mp4", writer=writer)


if __name__ == "__main__":
    main(
        gc_file=Path(
            "/Users/daniel/Desktop/DEV_cseproject/experiments/fraeseMit3/fraesen.cnc"
        ),
        audio_file=Path(
            "/Users/daniel/Desktop/DEV_cseproject/experiments/fraeseMit3/out.wav"
        ),
        parameter_file=Path(
            "/Users/daniel/Desktop/DEV_cseproject/experiments/fraeseMit3/readinfiles/parameter.txt"
        ),
        snapshot_file=Path(
            "/Users/daniel/Desktop/DEV_cseproject/experiments/fraeseMit3/readinfiles/snapshot_g_code.txt"
        ),
        out_directory=Path(
            "/Users/daniel/Desktop/DEV_cseproject/experiments/fraeseMit3"
        ),
        ramp_up_slope=60,
        ramp_down_slope=-60,
        hz_bound=1000,
    )
