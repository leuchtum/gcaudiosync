"""
This is the main entry point for the gcaudiosync module. It produces plots and a
video from the given input parameters. The main function `main()` reads in the
audio file and creates all the necessary  objects. It then analyses the G-Code
and converts the frequency information into. The function `plot_spec_raw()`
plots the base spectrogram and saves the figure if an outfile is specified. The
function `plot_spec_with_param_func()` plots the base spectrogram and the
guessed times and frequencies. It also saves the figure if an outfile is
specified. The function `debugger_is_active()` checks if the debugger is
currently active. 

The function `parse_args()` parses the command line arguments or uses default
values if the debugger is active. The main function `main()` calls the necessary
functions to perform pre-optimization and optimization of the guessed times and
frequencies. It also plots and saves the spectrogram after pre-optimization.

Note: This note only provides an overview of the functionality of the code. For
more detailed information, please refer to the comments within the code.
"""

import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib import animation
from matplotlib import pyplot as plt

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
from gcaudiosync.gcanalyser.gcanalyser import GCodeAnalyser
from gcaudiosync.gcanalyser.toolpathgenerator import AlternativeToolPathAnimator

PLOT = True


def _plot_base_spec(S, slicer, consts, ax, title):
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
    ax.set_title(title)


def plot_spec_raw(
    matrix: npt.NDArray[np.float64],
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
    matrix: npt.NDArray[np.float64],
    slicer: Slicer,
    consts: Constants,
    times: npt.NDArray[np.float64],
    freqs: npt.NDArray[np.float64],
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


def debugger_is_active():
    """Return if the debugger is currently active"""
    return hasattr(sys, "gettrace") and sys.gettrace() is not None


def parse_args():
    if debugger_is_active():
        gc_file = Path("gcode") / "Spindelhochlauf.cnc"
        audio_file = Path("sound") / "VID_20240103_125230.wav"
        parameter_file = Path("readinfiles") / "parameter.txt"
        snapshot_file = Path("readinfiles") / "snapshot_g_code.txt"
        ramp_up_slope = 60
        ramp_down_slope = -60
        hz_bound = 1000

    else:
        if len(sys.argv) != 8:
            msgs = [
                "Invalid number of arguments. Expected 7 arguments.",
                "",
                "Example usage:",
                "\t G-Code file: gcode/Spindelhochlauf.cnc",
                "\t Audio file: sound/VID_20240103_125230.wav",
                "\t Parameter file: readinfiles/parameter.txt",
                "\t Snapshot file: readinfiles/snapshot_g_code.txt",
                "\t Ramp up slope: 60",
                "\t Ramp down slope: -60",
                "\t Hz bound: 1000",
                "",
                "Results in:",
                "\tpython -m gcaudiosync gcode/Spindelhochlauf.cnc sound/VID_20240103_125230.wav readinfiles/parameter.txt readinfiles/snapshot_g_code.txt 60 -60 1000",
            ]
            raise ValueError("\n".join(msgs))

        gc_file = Path(sys.argv[1])
        audio_file = Path(sys.argv[2])
        parameter_file = Path(sys.argv[3])
        snapshot_file = Path(sys.argv[4])
        ramp_up_slope = float(sys.argv[5])
        ramp_down_slope = float(sys.argv[6])
        hz_bound = float(sys.argv[7])

    return {
        "gc_file": gc_file,
        "audio_file": audio_file,
        "parameter_file": parameter_file,
        "snapshot_file": snapshot_file,
        "ramp_up_slope": ramp_up_slope,
        "ramp_down_slope": ramp_down_slope,
        "hz_bound": hz_bound,
    }


def main():
    args = parse_args()

    # Read in the audio file and create all the necessary objects
    print("Reading in audio file...")
    rr = RawRecording.from_file(args["audio_file"])
    consts = Constants(rr.samplerate, rr.data)
    pr = ProcessedRecording(
        rr.data,
        n_fft=consts.n_fft,
        hop_length=consts.hop_length,
        win_length=consts.win_length,
    )

    # Create a G_Code_Analyser
    gc_analyser = GCodeAnalyser(
        parameter_src=args["parameter_file"],
        snapshot_src=args["snapshot_file"],
    )

    # Analyse G-Code
    print("Analysing G-Code...")
    gc_analyser.analyse(args["gc_file"])

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
    times_guess = np.concatenate((times_guess, [rr.duration]))
    freqs_guess = np.concatenate((freqs_guess, [0]))

    # Create parametrisable form function with the slopes specified. When
    # invoking the form function, the guessed times and frequencies will later
    # be used to create a parametrized form function.
    param_form_func = ParametrisableFormFunc(
        BendedSegmentBuilder(
            ramp_up_slope=args["ramp_up_slope"],
            ramp_down_slope=args["ramp_down_slope"],
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
    slice_to_freq_plot_only = np.argmax(
        consts.freqs > np.ceil(slice_to_freq / 1e3) * 1e3
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
            outfile=Path.cwd() / "spectrogram_unprocessed.png",
            title="Spektrogramm; nicht aufbereitet",
        )
        plot_spec_raw(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            outfile=Path.cwd() / "spectrogram_processed.png",
            title="Spektrogramm; aufbereitet",
        )
        plot_spec_with_param_func(
            pr.S_sqrt(),
            slicer_fac_plot_only.build(),
            consts,
            times_guess,
            freqs_guess,
            param_form_func,
            outfile=Path.cwd() / "spectrogram_with_guesses.png",
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
            outfile=Path.cwd() / "spectrogram_with_preoptimized_guesses.png",
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
            outfile=Path.cwd() / "spectrogram_with_optimized_guesses.png",
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
    start_time = times_guess[1]
    total_time = times_guess[-2] - start_time
    gc_analyser.set_start_time_and_total_time(start_time * 1000, total_time * 1000)
    for freq_info, gc_timestamp in zip(freq_infos[:-1], times_guess[:-2]):
        gc_index = freq_info.g_code_line_index_start
        gc_analyser.adjust_start_time_of_g_code_line(gc_index, 1000 * gc_timestamp)

    # Plot the tool path. For this we crate an animation, which will be saved as
    # an mp4 file. We animate via two Animator objects, one for the tool path
    # and one for the spectrogram. Then the callback function is used to update
    # each frame.
    if PLOT:
        print("Plotting and saving tool path...")
        fps = 26
        fig = plt.figure(figsize=(15, 5))
        ax_info = fig.add_subplot(1, 6, 1)
        ax_tool = fig.add_subplot(1, 6, (2, 3))
        ax_spec = fig.add_subplot(1, 6, (4, 6))
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
            consts=consts,
            ax=ax_spec,
            global_slice_cfg=ValueSlicerConfig(
                from_y=0,
                to_y=args["hz_bound"],
            ),
        )

        def callback(frame_s: float):
            plt_objs = []
            plt_objs.append(toolpath_ani.callback(frame_s))
            plt_objs.append(spec_ani.callback(frame_s))
            return plt_objs

        frames = np.linspace(0, spec_ani.total_time, spec_ani.nof_frames)
        time_diff_in_millis = 1000 / fps
        anim = animation.FuncAnimation(
            fig,
            callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        fig.tight_layout()
        writer = animation.FFMpegWriter(fps=fps)
        anim.save(Path.cwd() / "toolpath_with_spectrogram.mp4", writer=writer)


if __name__ == "__main__":
    main()
