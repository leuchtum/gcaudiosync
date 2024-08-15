import sys
from pathlib import Path

from matplotlib import pyplot as plt

from gcaudiosync.audioanalyser.constants import Constants
from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import LazyProcessedRecording
from gcaudiosync.audioanalyser.visualize import add_footnote, spectrogram


def run(file: Path):
    rr = RawRecording.from_file(file)
    consts = Constants(rr.samplerate, rr.data)
    pr = LazyProcessedRecording(
        rr.data,
        n_fft=consts.n_fft,
        hop_length=consts.hop_length,
        win_length=consts.win_length,
    )

    X = pr.S_db()
    span = X.max() - X.min()
    X[X < (X.min() + 0.33 * span)] = X.min()
    X[X > (X.min() + 0.66 * span)] = X.max()
    fig, ax = plt.subplots(figsize=(14, 8))
    ax = spectrogram(pr.S_db(), consts, is_db=True, y_axis="linear", ax=ax)
    note = f"File: {file.name}\n" f"X.shape: {pr.S_db().shape}"
    ax = add_footnote(ax, note, loc="left")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(Path("spectros") / file.with_suffix(".png").name, format="png")


if len(sys.argv) == 1:
    file = Path("sound/VID_20240103_125230.wav")
    run(file)
else:
    for file in sys.argv[1:]:
        run(Path(file))
