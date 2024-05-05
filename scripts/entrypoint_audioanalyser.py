from pathlib import Path

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.signalprocessing import ProcessedRecording

root_dir = Path("/Users/daniel/Desktop/WD_cseproject/")
file_name = "VID_20240221_201705.wav"
file = root_dir / file_name

rr = RawRecording.from_file(file)
pr = ProcessedRecording.from_raw(rr)

pass
