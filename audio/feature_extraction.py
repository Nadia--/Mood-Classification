# Project Libraries

# General Libraries
import glob
import librosa
import numpy as np
import math

"""
API for extracting various features from audio tracks
Currently supporting: MFCCs, Spectral Centroids
"""

BASE_DIRECTORY = "./../data/youtube_data/songs/"

DFT_SIZE = 2048
HOP_SIZE = 512
ZERO_PAD = 0


def get_audio(video_id):
    """ Returns local audio file name based on its YouTube video id"""

    fileglob = BASE_DIRECTORY + ("%s.*.mp3" % video_id)
    audio_file_name = glob.glob(fileglob)[0]
    print(audio_file_name)
    return librosa.load(audio_file_name)


def stft(input_array, dft_size, hop_size, zero_pad, window):
    """
    Returns either the short time fourier transform of an audio track,
    or the audio track corresponding to a short time fourier transform.

    :param input_array: either a 1d array of audio samples, or a 2d stft array
    :param dft_size: the number of samples in a frame
    :param hop_size: the difference between the beginnings of frames (preferably 1/4 of dtf_size)
    :param zero_pad: the number of 0-valued samples to append to the sides of a frame(must be a multiple of 2)
    :param window: the type of window
    :return: either a 2d stft array [time][freq], or 1d audio array, respectively corresponding to input_array
    """

    # Forward Transform (Wave -> STFT)
    if (input_array.ndim == 1):

        # pad dft_size/2 zeros to the beginning and end of the sound to prevent window from annihilating the intensities
        pad = np.zeros(math.ceil(dft_size / 2))
        padded_sound = np.concatenate((pad, input_array, pad))

        # pad input_sound to make final frame full-length
        num_hops = math.floor(len(padded_sound) / hop_size)
        num_to_pad = len(padded_sound) - num_hops * hop_size
        squared_sound = np.append(padded_sound, [0] * num_to_pad)

        # taking slices of audio to create frames
        truncated_length = len(squared_sound) - dft_size
        frames = np.array(
            [squared_sound[idx:idx + dft_size] * window for idx in range(truncated_length) if idx % hop_size == 0])

        # fourier transform of each frame
        pad = np.zeros(math.ceil(zero_pad / 2))
        fft = np.array([np.fft.rfft(np.concatenate((pad, frame, pad))) for frame in frames])

        return fft

    # Inverse Transform (STFT -> Wave)
    elif (input_array.ndim == 2):
        inverse = np.array([np.fft.irfft(frame, dft_size) for frame in input_array])

        # TODO: fix slight sound length mismatch :c
        len_sound = hop_size * len(inverse) + dft_size
        restored_sound = [0] * len_sound

        for idx, frame in enumerate(inverse):
            flat = idx * (hop_size - 1)
            restored_sound[flat:flat + dft_size] += frame * window

        # remove beginning and ending pads
        pad_len = math.ceil(dft_size / 2)
        return np.array(restored_sound[pad_len:len(restored_sound) - pad_len])

    else:
        return None


def get_spectral_flux(y, sr, n_fft, hop_length):
    """ Returns a measure of variance in frequencies over time"""
    # TODO: should incorporate sampling rate and use the same sampling rate for all

    stfts = abs(stft(y, n_fft, hop_length, ZERO_PAD, np.hanning(n_fft)))
    time_points = len(stfts)

    spect_flux = np.array([np.average((stfts[i] - stfts[i - 1]) ** 2) for i in range(time_points)])

    package = np.zeros((1, len(spect_flux)))
    package[0] = spect_flux
    return package


def extract_features(audio, sr, mfcc=True, spectral_centroid=True, spectral_flux=True, num_mfccs=20):
    """
    Extracts audio features per frame of audio track

    :param audio: the audio time series
    :param sr: the sampling rate of the audio
    :param mfcc: whether to extract mfcc feature
    :param spectral_centroid: whether to extract spectral centroid feature
    :param spectral_flux: whether to extract spectral flux feature
    """
    feats = [None]*3

    if mfcc:
        feats[0] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs, n_fft=DFT_SIZE, hop_length=HOP_SIZE)
    if spectral_centroid:
        feats[1] = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=DFT_SIZE, hop_length=HOP_SIZE)
    if spectral_flux:
        feats[2] = get_spectral_flux(y=audio, sr=sr, n_fft=DFT_SIZE, hop_length=HOP_SIZE)

    feats = [feat for feat in feats if feat is not None]

    features = np.concatenate(tuple(feats))
    return np.swapaxes(features, 0, 1)

