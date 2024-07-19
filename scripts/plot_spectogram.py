import sys
from pathlib import Path

from matplotlib import pyplot as plt

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import LazyProcessedRecording
from gcaudiosync.audioanalyser.visualize import add_footnote, spectrogram


def run(file: Path):
    rr = RawRecording.from_file(file)
    pr = LazyProcessedRecording(data=rr.data, samplerate=rr.samplerate)

    X = pr.S_db()
    span = X.max() - X.min()
    X[X < (X.min() + 0.33 * span)] = X.min()
    X[X > (X.min() + 0.66 * span)] = X.max()
    fig, ax = plt.subplots(figsize=(14, 8))
    ax = spectrogram(pr.S_db(), pr.samplerate, is_db=True, y_axis="log", ax=ax)
    note = f"File: {file.name}\n" f"X.shape: {pr.S_db().shape}"
    ax = add_footnote(ax, note, loc="left")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(Path("spectros") / file.with_suffix(".png").name, format="png")


if len(sys.argv) == 1:
    file = Path("generated_tones/tone2.wav")
    run(file)
else:
    for file in sys.argv[1:]:
        run(Path(file))
