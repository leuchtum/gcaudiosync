import uuid
from pathlib import Path

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import ProcessedRecording
from gcaudiosync.audioanalyser.visualize import add_footnote, spectrogram

root_dir = Path("/Users/daniel/Desktop/WD_cseproject/")
file_name = "VID_20240221_201705.wav"
file = root_dir / file_name

rr = RawRecording.from_file(file)
pr = ProcessedRecording.from_raw(rr)

ax = spectrogram(pr.S_db, pr.samplerate, is_db=True, y_axis="log")
note = f"File: {file_name}\n" f"X.shape: {pr.S_db.shape}"
ax = add_footnote(ax, note, loc="left")
fig = ax.get_figure()
fig.tight_layout()
fig.savefig(f"{uuid.uuid4()}.png", format="png")

pass
