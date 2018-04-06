import numpy as np
from numpy.lib import stride_tricks
import scipy.io.wavfile as wav
from matplotlib import pyplot as plt

FPS = 24


def logscale_spec(spec, sr=44100, buckets=200):
    """ scale frequency axis logarithmically """
    timebins, freqbins = np.shape(spec)

    scale = np.exp(np.log(freqbins) * np.arange(buckets) / buckets)
    print(scale)
    scale = np.unique(np.round(scale)).astype(int)
    print(scale)

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, scale[i]:], axis=1)
        else:
            newspec[:, i] = np.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.sum(allfreqs[scale[i]:])]
        else:
            freqs += [np.sum(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs


def spectrogram(audio_path, buckets, fps=FPS, fft_window_size=2**11):
    """
    :param audio_path: 
    :param buckets: number of buckets for spectrogram
    :param fps: frames per second
    :param fft_window_size: window size for fourier transform
    :return: logarithmic spectrum
    """
    rate, audio = wav.read(audio_path)
    print("Length in seconds: ", audio.shape[0] / rate)

    # size of window to have fps number of frames per second
    window_size = fft_window_size

    # smooth window for sliding convolution
    smooth_window = np.hanning(window_size)

    # size we step in the signal between windows
    hop_size = int(rate / fps)

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.int(window_size / 2.0)), audio)

    # number of windows
    number_of_columns = np.int((len(samples) - window_size) / float(hop_size)) + 1

    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(window_size))

    # chop up sample into windows for Fourier transform
    frames = stride_tricks.as_strided(samples, shape=(number_of_columns, window_size),
                                      strides=(samples.strides[0] * hop_size, samples.strides[0])).copy()

    # smooth out the windows
    frames *= smooth_window

    # do the Fourier transform
    fourier = np.fft.rfft(frames)
    print(fourier.shape)

    log_spectrogram, _ = logscale_spec(fourier, buckets=buckets)
    #
    log_spectrogram = np.log(np.abs(log_spectrogram) + 1)
    print(log_spectrogram.shape)
    #
    plt.imshow(np.transpose(log_spectrogram), cmap='hot', interpolation='nearest', aspect='auto')
    plt.show()
    return np.flipud(log_spectrogram)


NUMBER_OF_LEVELS = 30
AUDIO_PATH = "C:/Users/Yegreg/PycharmProjects/Blender scripts/eightfold.wav"
spec = spectrogram(AUDIO_PATH, NUMBER_OF_LEVELS)
# spec -= np.min(spec, axis=0)
# spec /= np.max(spec, axis=0)
length, number_of_levels = spec.shape
max_spec = spec.copy()
for i in range(12, length):
    max_spec[i, :] = np.max(spec[i - 12: i, :], axis=0)

np.savez("eightfold.npz", spec=spec, max_spec=max_spec)
