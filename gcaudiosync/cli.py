"""This file contains the command line interface for the gcaudiosync package."""

from pathlib import Path

import click


@click.group()
def cli() -> None:
    pass


@cli.command()
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
def analyse(
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

    msg = "\n".join(
        (
            "Input:",
            f"\t- G-code file: {gc_file}",
            f"\t- Audio file: {audio_file}",
            f"\t- Parameter file: {parameter_file}",
            f"\t- Snapshot file: {snapshot_file}",
            f"\t- Output directory: {out_directory}",
            f"\t- Ramp-up slope: {ramp_up_slope} Hz/s",
            f"\t- Ramp-down slope: {ramp_down_slope} Hz/s",
            f"\t- Hz-bound: {hz_bound} Hz",
        )
    )
    click.echo(msg)
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


@cli.command()
@click.option(
    "--audio",
    "audio_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="The audio file to be analyzed.",
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
    "--slope",
    "slope",
    type=float,
    help="The acceleration/deceleration of the main tool spindle in Hz/s. Carry the minus sign for deceleration!",
    required=True,
)
@click.option(
    "--hz-bound",
    "hz_bound",
    type=float,
    help="The upper frequency that still will be plotted.",
    required=True,
)
@click.option(
    "--n-stripes",
    "n_stripes",
    type=int,
    help="The number of stripes to be plotted.",
    required=True,
)
def slope(
    audio_file: Path,
    out_directory: Path,
    slope: float,
    hz_bound: float,
    n_stripes: int,
) -> None:
    from gcaudiosync import plot_spectrogram_with_slope

    plot_spectrogram_with_slope.main(
        audio_file=audio_file,
        out_directory=out_directory,
        slope=slope,
        hz_bound=hz_bound,
        n_stripes=n_stripes,
    )


if __name__ == "__main__":
    cli()
