# Project Libraries
from feature_extraction import get_audio
from feature_extraction import get_spectral_flux
from feature_extraction import extract_features

# General Libraries
from unittest import TestCase


class TestFeatureExtraction(TestCase):
    def test_get_audio(self):
        audio, sr = get_audio('yzTuBuRdAyA')
        self.assertEqual(sr, 48000, "sampling rate loaded")
        self.assertEqual(len(audio), 11241185, "audio length")

    def test_spectral_flux(self):
        audio, sr = get_audio('yzTuBuRdAyA')
        spectral_flux = get_spectral_flux(audio, sr, n_fft=1024, hop_length=256)
        self.assertEqual((1, 43911), spectral_flux.shape, "spectral flux shape")

    def test_feature_extraction(self):
        audio, sr = get_audio('lIYCHbOTab4')

        result = extract_features(audio, sr)
        self.assertEqual((22, 18424), result.shape, "frame features extraction")

        result2 = extract_features(audio, sr, mfcc=False)
        self.assertEqual((2, 18424), result2.shape, "frame features extraction")


