# Project Libraries
from feature_extraction import get_audio
from feature_extraction import get_spectral_flux
from feature_extraction import extract_features

# General Libraries
from unittest import TestCase


class TestFeatureExtraction(TestCase):
    def test_get_audio(self):
        audio, sr = get_audio('yzTuBuRdAyA')
        self.assertEqual(sr, 22050, "sampling rate loaded")
        self.assertEqual(len(audio), 5163920, "audio length")

    def test_spectral_flux(self):
        audio, sr = get_audio('yzTuBuRdAyA')
        spectral_flux = get_spectral_flux(audio, sr)
        self.assertEqual(len(spectral_flux), 513, "spectral flux shape")

    def test_feature_extraction(self):
        video_ids = ['lIYCHbOTab4', 'yzTuBuRdAyA']

        mfccs, spectral_centroids, spectral_fluxes = \
            extract_features(video_ids, mfcc=True, spectral_centroid=False, spectral_flux=False)
        self.assertIsNone(spectral_centroids, "feature is none")
        self.assertIsNone(spectral_fluxes, "feature is none")
        self.assertIsNotNone(mfccs, "feature is not none")

        mfccs, spectral_centroids, spectral_fluxes = extract_features(video_ids)

        song = 0
        self.assertEqual(mfccs[song].shape, (20, 8464), "mfccs shape")
        self.assertEqual(spectral_centroids[song].shape, (1, 8464), "spectral centroids shape")
        self.assertEqual(spectral_fluxes[song].shape, (513,), "spectral fluxes shape")

        song = 1
        self.assertEqual(mfccs[song].shape, (20, 10086), "mfccs shape")
        self.assertEqual(spectral_centroids[song].shape, (1, 10086), "spectral centroids shape")
        self.assertEqual(spectral_fluxes[song].shape, (513,), "spectral fluxes shape")



