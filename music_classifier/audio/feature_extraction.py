# Project Libraries

# General Libraries
import librosa
import numpy as np
import os
import json

"""
API for extracting various features from audio tracks
Currently supporting: MFCCs, Spectral Centroid, Spectral Flux
"""


FEATURES_CACHE_DIRECTORY = "./../data/features_cache/"


def cache_directory(extension, base=FEATURES_CACHE_DIRECTORY):
    directory = base + extension + '/'
    if not os.path.exists(directory):
        print("Making directory: %s" % directory)
        os.makedirs(directory)

    return directory


def read_dictionary(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        dictionary = json.loads(f.read())
    return dictionary


def write_dictionary(filename, dictionary):
    with open(filename, 'w') as fp:
        json.dump(dictionary, fp)

def write_feats_dictionary(filename, dictionary):
    serialized_dictionary = {key: value.tolist() for (key, value) in dictionary.items()}
    write_dictionary(filename, serialized_dictionary)

def read_feats_dictionary(filename):
    serialized_dictionary = read_dictionary(filename)
    return {key: np.array(value) for (key, value) in serialized_dictionary.items()}


class pSTFT:
    def __init__(self, dft_dur, hop_ratio):
        self.dft_dur = dft_dur
        self.hop_ratio = hop_ratio

    def dir_name(self):
        return "d%.2f_h%.2f" % (self.dft_dur, self.hop_ratio)

    def dft_size(self, sr):
        return round(sr * self.dft_dur)

    def hop_size(self, sr):
        return round(sr * self.dft_dur * self.hop_ratio)

    def __repr__(self):
        return "STFT(dft:%.2f,hop:%.2f)" % (self.dft_dur, self.hop_ratio)


class pFeats:
    def __init__(self, mfcc=False, spectral_centroid=False, spectral_flux=False):
        self.mfcc = mfcc
        self.spectral_centroid = spectral_centroid
        self.spectral_flux = spectral_flux

    def __repr__(self):
        repr = "Comb("
        if self.mfcc:
            repr += "mfcc,"
        if self.spectral_centroid:
            repr += "cent,"
        if self.spectral_flux:
            repr += "flux,"

        return repr[:-1] + ")"

def get_spectral_flux(y, n_fft, hop_length):
    """ Returns a measure of variance in frequencies over time"""

    stfts = abs(librosa.core.stft(y, n_fft, hop_length))
    stfts = np.swapaxes(stfts, 0, 1)

    spect_flux = np.array([np.average((stfts[i] - stfts[i - 1]) ** 2) for i in range(len(stfts))])

    package = np.zeros((1, len(spect_flux)))
    package[0] = spect_flux
    return package


def feature_dict_name(stft_dir, feature, dict_name):
    cache_directory(feature, base=stft_dir)
    return stft_dir + feature + '/' + dict_name


def maybe_dictionary(need_extract, path):
    if not need_extract:
        return None

    if os.path.exists(path):
        # No need to extract if already cached
        return None

    return {}


def extract_features_to_cache(stft_dir, stft_par, examples, music_data_dir, feat_combs, num_mfccs_pars):
    extraction_needed = False

    # Determine What Needs Extracting
    extract_mfccs = any(list(map(lambda feat_comb: feat_comb.mfcc, feat_combs)))
    extract_spectral_centroids = any(list(map(lambda feat_comb: feat_comb.spectral_centroid, feat_combs)))
    extract_spectral_flux = any(list(map(lambda feat_comb: feat_comb.spectral_flux, feat_combs)))

    mfccs_sub_dictionary = [None]*len(num_mfccs_pars)
    for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
        mfccs_sub_dictionary[nm_idx] = maybe_dictionary(extract_mfccs, feature_dict_name(stft_dir, "MFCC", str(num_mfccs)))
        if mfccs_sub_dictionary[nm_idx] is not None:
            extraction_needed = True

    spect_cent_dictionary = maybe_dictionary(extract_spectral_centroids, feature_dict_name(stft_dir, "SPECT_CENT", 'default'))
    spect_flux_dictionary = maybe_dictionary(extract_spectral_flux, feature_dict_name(stft_dir, "SPECT_FLUX", 'default'))
    if spect_cent_dictionary is not None or spect_flux_dictionary is not None:
        extraction_needed = True

    if not extraction_needed:
        return

    # Extract Features
    counter = 0
    for song_idx, song in enumerate(examples):

        audio, sr = librosa.load(music_data_dir + '/songs/' + song, sr=None)
        dft_size = stft_par.dft_size(sr)
        hop_size = stft_par.hop_size(sr)

        # TODO: re-use stft between feature extractions

        for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
            if mfccs_sub_dictionary[nm_idx] is not None:
                mfccs_sub_dictionary[nm_idx][song] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=num_mfccs, n_fft=dft_size, hop_length=hop_size)

        if spect_cent_dictionary is not None:
            spect_cent_dictionary[song] = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=dft_size, hop_length=hop_size)

        if spect_flux_dictionary is not None:
            spect_flux_dictionary[song] = get_spectral_flux(y=audio, n_fft=dft_size, hop_length=hop_size)

        counter += 1
        print("Feature Extraction Progress: %d%%" % (counter/len(examples) * 100))

    # Write Feature Files
    print("Writing Feature Files...")
    for nm_idx, num_mfccs in enumerate(num_mfccs_pars):
        if mfccs_sub_dictionary[nm_idx] is not None:
            write_feats_dictionary(feature_dict_name(stft_dir, "MFCC", str(num_mfccs)), mfccs_sub_dictionary[nm_idx])
    if spect_cent_dictionary is not None:
        write_feats_dictionary(feature_dict_name(stft_dir, "SPECT_CENT", 'default'), spect_cent_dictionary)
    if spect_flux_dictionary is not None:
        write_feats_dictionary(feature_dict_name(stft_dir, "SPECT_FLUX", 'default'), spect_flux_dictionary)


