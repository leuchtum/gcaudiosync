from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, kw_only=True)
class SoundData:
    samplerate: int
    data: np.ndarray

    @property
    def duration(self) -> float:
        return self.nsamples / self.samplerate

    @property
    def nsamples(self) -> int:
        return self.data.shape[0]

    @property
    def nchannels(self) -> int:
        return 1 if len(self.data.shape) == 1 else self.data.shape[1]

    def split_at_indices(self, indices: list[int]) -> list["SoundData"]:
        return [
            SoundData(samplerate=self.samplerate, data=self.data[start:end])
            for start, end in zip([0, *indices], [*indices, self.nsamples])
        ]
