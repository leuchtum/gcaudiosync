from pathlib import Path

from scipy.io import wavfile

from gcaudiosync.sound import SoundData


def read_wav_file(file_path: str | Path) -> SoundData:
    srate, data = wavfile.read(file_path)
    return SoundData(samplerate=srate, data=data)
