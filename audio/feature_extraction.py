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

DFT_SIZE = 1024
HOP_SIZE = 256
ZERO_PAD = 0
WINDOW = np.hanning(DFT_SIZE)


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

def get_spectral_flux(audio, sr):
    """ Returns a measure of variance in frequencies over time"""
    #TODO: should incorporate sampling rate and use the same sampling rate for all

    stfts = abs(stft(audio, DFT_SIZE, HOP_SIZE, ZERO_PAD, WINDOW))

    time_points = len(stfts)
    frequencies = len(stfts[0])

    spect_flux = [0]*frequencies

    for i in range(time_points-1):
        diffs_squared = (stfts[i] - stfts[i+1])**2
        spect_flux += diffs_squared / (time_points-1)

    return spect_flux


def extract_features(video_ids, mfcc=True, spectral_centroid=True, spectral_flux=True, num_mfccs=20):
    """
    Extracts audio features from audio tracks corresponding to YouTube video ids

    :param video_ids: the video ids of the audio tracks we're interested in
    :param mfcc: whether to extract mfcc feature
    :param spectral_centroid: whether to extract spectral centroid feature
    :return: extracted features
    """

    mfccs = None
    spectral_centroids = None
    spectral_fluxes = None

    if mfcc:
        mfccs = [0] * len(video_ids)
    if spectral_centroid:
        spectral_centroids = [0] * len(video_ids)
    if spectral_flux:
        spectral_fluxes = [0] * len(video_ids)

    for idx, video_id in enumerate(video_ids):
        audio, sr = get_audio(video_id)
        print(sr)

        if mfcc:
            mfccs[idx] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs)
        if spectral_centroid:
            spectral_centroids[idx] = librosa.feature.spectral_centroid(y=audio, sr=sr)
        if spectral_flux:
            spectral_fluxes[idx] = get_spectral_flux(audio, sr)

    return mfccs, spectral_centroids, spectral_fluxes

