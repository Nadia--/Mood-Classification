# Project Libraries

# General Libraries
import glob
import librosa
import numpy as np
import math

"""
API for extracting various features from audio tracks
Currently supporting: MFCCs, Spectral Centroid, Spectral Flux
"""

BASE_DIRECTORY = "./../data/youtube_data/songs/"

DFT_SIZE = 2048
HOP_SIZE = 512


def get_audio(video_id):
    """ Returns local audio file name based on its YouTube video id"""

    fileglob = BASE_DIRECTORY + ("%s.*.mp3" % video_id)
    audio_file_name = glob.glob(fileglob)[0]
    print(audio_file_name)
    return librosa.load(audio_file_name)

def get_spectral_flux(y, sr, n_fft, hop_length):
    """ Returns a measure of variance in frequencies over time"""
    # TODO: should incorporate sampling rate and use the same sampling rate for all

    stfts = abs(librosa.core.stft(y, n_fft, hop_length))
    stfts = np.swapaxes(stfts, 0, 1)

    spect_flux = np.array([np.average((stfts[i] - stfts[i - 1]) ** 2) for i in range(len(stfts))])

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
    feats = [None] * 3

    if mfcc:
        feats[0] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs, n_fft=DFT_SIZE, hop_length=HOP_SIZE)
    if spectral_centroid:
        feats[1] = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=DFT_SIZE, hop_length=HOP_SIZE)
    if spectral_flux:
        feats[2] = get_spectral_flux(y=audio, sr=sr, n_fft=DFT_SIZE, hop_length=HOP_SIZE)

    feats = [feat for feat in feats if feat is not None]

    features = np.concatenate(tuple(feats))
    return np.swapaxes(features, 0, 1)
