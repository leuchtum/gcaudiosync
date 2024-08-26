from pathlib import Path
import re

import click


@click.command()
@click.option(
    "--gcode",
    "gc_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="The G-code file to be analyzed.",
    required=True,
)
@click.option(
    "--audio",
    "audio_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="The audio file to be analyzed.",
    required=True,
)
@click.option(
    "--parameter",
    "parameter_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="The parameter file for the specific machine.",
    required=True,
)
@click.option(
    "--snapshot",
    "snapshot_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="The file where the snapshot is specified.",
    required=True,
)
@click.option(
    "--output-directory",
    "out_directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
    help="The directory where the output files will be saved.",
    required=True,
)
@click.option(
    "--ramp-up",
    "ramp_up_slope",
    type=float,
    help="The acceleration of the main tool spindle in Hz/s.",
    required=True,
)
@click.option(
    "--ramp-down",
    "ramp_down_slope",
    type=float,
    help="The deceleration of the main tool spindle in Hz/s. Carry the minus sign!",
    required=True,
)
@click.option(
    "--hz-bound",
    "hz_bound",
    type=float,
    help="The upper frequency that still will be plotted.",
    required=True,
)
def main(
    gc_file: Path,
    audio_file: Path,
    parameter_file: Path,
    snapshot_file: Path,
    out_directory: Path,
    ramp_up_slope: float,
    ramp_down_slope: float,
    hz_bound: float,
) -> None:
    from gcaudiosync import core

    core.main(
        gc_file=gc_file,
        audio_file=audio_file,
        parameter_file=parameter_file,
        snapshot_file=snapshot_file,
        out_directory=out_directory,
        ramp_up_slope=ramp_up_slope,
        ramp_down_slope=ramp_down_slope,
        hz_bound=hz_bound,
    )


if __name__ == "__main__":
    main()
