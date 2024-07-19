from pathlib import Path

from gcaudiosync.audioanalyser.io import RawRecording
from gcaudiosync.audioanalyser.preprocessing import PreprocessedRecording
from gcaudiosync.audioanalyser.signalprocessing import LazyProcessedRecording

root_dir = Path("/Users/daniel/Desktop/WD_cseproject/")
file_name = "VID_20240221_201705.wav"
file = root_dir / file_name

rr = RawRecording.from_file(file)
ppr = PreprocessedRecording(data=rr.data, samplerate=rr.samplerate)
ppr.filter_out_silence()
pr = LazyProcessedRecording(data=ppr.data, samplerate=ppr.samplerate)

pr.abc_filter()
pr.harmonic_filtered_dominant_freq()

pass
