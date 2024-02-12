from pathlib import Path

import gaudiosync.io

file_path = Path("/Users/daniel/Desktop/WD_cse_project/VID_20240103_125230_MONO.wav")

sound_data = gaudiosync.io.read_wav_file(file_path)
print(sound_data.nchannels)
