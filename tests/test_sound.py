import numpy as np

from gaudiosync.sound import SoundData


def test_sound_data_properties():
    data = np.array([1, 2, 3, 4, 5])
    samplerate = 44100
    sound_data = SoundData(samplerate=samplerate, data=data)

    assert sound_data.samplerate == samplerate
    assert np.array_equal(sound_data.data, data)
    assert sound_data.duration == len(data) / samplerate
    assert sound_data.nsamples == len(data)
    assert sound_data.nchannels == 1


def test_sound_data_split_at_indices():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    samplerate = 44100
    sound_data = SoundData(samplerate=samplerate, data=data)

    indices = [2, 5, 8]
    split_data = sound_data.split_at_indices(indices)

    assert len(split_data) == len(indices) + 1
    assert np.array_equal(split_data[0].data, data[: indices[0]])
    assert np.array_equal(split_data[1].data, data[indices[0] : indices[1]])
    assert np.array_equal(split_data[2].data, data[indices[1] : indices[2]])
    assert np.array_equal(split_data[3].data, data[indices[2] :])
