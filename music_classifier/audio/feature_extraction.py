# Project Libraries

# General Libraries
import glob
import librosa
import numpy as np
import os
import json

"""
API for extracting various features from audio tracks
Currently supporting: MFCCs, Spectral Centroid, Spectral Flux
"""

# BASE_DIRECTORY = "./../data/youtube_data/songs/"

BASE_DIRECTORY = "./../data/features_cache/"

def load_audio_file(file_name):
    """ Loads local audio track based on file name """
    audio, sr = librosa.load(file_name, sr=48000)  # Most files have this sampling rate natively
    return audio, sr

def get_audio(video_id):
    """ Loads local audio track name based on its YouTube video id"""

    fileglob = BASE_DIRECTORY + ("%s.*.mp3" % video_id)
    audio_file_name = glob.glob(fileglob)[0]
    print(audio_file_name)
    return load_audio_file(audio_file_name)

def prepare_directory(folder_list):
    directory = BASE_DIRECTORY + '/'.join(folder_list)
    print(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory

def load_dictionary(filename):
    with open(filename, 'r') as f:
        dictionary = json.loads(f.read())
    return dictionary

def write_dictionary(filename, dictionary):
    with open(filename, 'w') as fp:
        json.dump(dictionary, fp)

class pSTFT:
    def __init__(self, dft_dur, hop_ratio):
        self.dft_dur = dft_dur
        self.hop_ratio = hop_ratio

    def dirname(self):
        return "d%.2f_h%.2f" % (self.dft_dur, self.hop_ratio)

    def dft_size(self, sr):
        return round(sr * self.dft_dur)

    def hop_size(self, sr):
        return round(sr * self.dft_dur * self.hop_ratio)

class pFeats:
    def __init__(self, mfcc=False, spectral_centroid=False, spectral_flux=False):
        self.mfcc = mfcc
        self.spectral_centroid = spectral_centroid
        self.spectra_flux = spectral_flux


def get_spectral_flux(y, sr, n_fft, hop_length):
    """ Returns a measure of variance in frequencies over time"""
    # TODO: should incorporate sampling rate and use the same sampling rate for all

    stfts = abs(librosa.core.stft(y, n_fft, hop_length))
    stfts = np.swapaxes(stfts, 0, 1)

    spect_flux = np.array([np.average((stfts[i] - stfts[i - 1]) ** 2) for i in range(len(stfts))])

    package = np.zeros((1, len(spect_flux)))
    package[0] = spect_flux
    return package

def feature_dict_name(stft_dir, feature, dict_name):
    return stft_dir + '/' + feature + '/' + dict_name

def init_feature_dictionary(stft_dir, feature, dict_name, need_extract):
    path = feature_dict_name(stft_dir, feature, dict_name)
    dictionary = None

    if need_extract:
        if os.path.exists(path):
            dictionary = {}
    return dictionary

def prepare_features(stft_dir, stft_par, examples, feat_combs, num_mfccs_pars):

    # Determine What Needs Extracting
    extract_mfccs = any(list(map(lambda feat_comb: feat_comb.mfcc, feat_combs)))
    extract_spectral_centroids = any(list(map(lambda feat_comb: feat_comb.spectral_centroid, feat_combs)))
    extract_spectral_flux = any(list(map(lambda feat_comb: feat_comb.spectral_flux, feat_combs)))

    mfccs_sub_dictionary = [None]*len(num_mfccs_pars)
    for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
        mfccs_sub_dictionary[nm_idx] = init_feature_dictionary(stft_dir, "MFCC", num_mfccs, extract_mfccs)

    spect_cent_dictionary = init_feature_dictionary(stft_dir, "SPECT_CENT", 'default', extract_spectral_centroids)
    spect_flux_dictionary = init_feature_dictionary(stft_dir, "SPECT_FLUX", 'default', extract_spectral_flux)

    # Extract Features
    for song in examples:
        audio, sr = librosa.load(song, sr=None) # TODO: directory or some shit
        dft_size = stft_par.get_dft_size(sr)
        hop_size = stft_par.get_hop_size(sr)

        # TODO: re-use stft between feature extractions

        for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
            if mfccs_sub_dictionary[nm_idx] is not None:
                mfccs_sub_feat = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs, n_fft=dft_size, hop_length=hop_size)
                mfccs_sub_dictionary[nm_idx][song] = mfccs_sub_feat

        if spect_cent_dictionary is not None:
            spect_cent_feat = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=dft_size, hop_length=hop_size)
            spect_cent_dictionary[song] = spect_cent_feat

        if spect_flux_dictionary is not None:
            spect_flux_feat = get_spectral_flux(y=audio, sr=sr, n_fft=dft_size, hop_length=hop_size)
            spect_flux_dictionary[song] = spect_flux_feat

    # Write Feature Files
    for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
        if mfccs_sub_dictionary[nm_idx] is not None:
            write_dictionary(feature_dict_name(stft_dir, "MFCC", num_mfccs), mfccs_sub_dictionary[nm_idx])
    if spect_cent_dictionary is not None:
        write_dictionary(feature_dict_name(stft_dir, "SPECT_CENT", 'default'), spect_cent_dictionary)
    if spect_flux_dictionary is not None:
        write_dictionary(feature_dict_name(stft_dir, "SPECT_FLUX", 'default'), spect_flux_dictionary)



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
    return features
