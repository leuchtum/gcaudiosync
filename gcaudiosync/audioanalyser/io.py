from pathlib import Path

import librosa


class RawRecording:
    """Class that holds the raw recording data."""

    def __init__(self, file_path: Path) -> None:
        self.rough_samplerate = librosa.get_samplerate(path=file_path)
        self.rough_duration = librosa.get_duration(path=file_path)
        self.data, self.samplerate = librosa.load(path=file_path)
