from dataclasses import dataclass
from pathlib import Path
from typing import Self

import librosa
import numpy as np
import numpy.typing as npt


@dataclass
class RawRecording:
    """
    Represents a raw audio recording.

    Attributes:
        data (ndarray): The audio data as a NumPy array of float32 values.
        samplerate (float): The sample rate of the audio recording.
        duration (float): The duration of the audio recording in seconds.
    Methods:
        from_file(file_path: Path, **kwargs) -> RawRecording:
            Creates a RawRecording object from an audio file.
            Args:
                file_path (Path): The path to the audio file.
                **kwargs: Additional keyword arguments for loading the audio
                file.
                RawRecording: The created RawRecording object.
            Raises:
                ValueError: If the given duration is greater than the duration
                of the file.
    """

    data: npt.NDArray[np.float32]
    samplerate: float
    duration: float

    @classmethod
    def from_file(cls, file_path: Path, **kwargs) -> Self:
        file_sr = librosa.get_samplerate(file_path)
        file_duration = librosa.get_duration(path=file_path)
        if "sr" not in kwargs:
            kwargs["sr"] = file_sr
        if "duration" in kwargs and kwargs["duration"] > file_duration:
            msg = "Given duration is greater than the duration of the file"
            raise ValueError(msg)
        data, samplerate = librosa.load(file_path, **kwargs)
        return cls(data=data, samplerate=samplerate, duration=file_duration)
