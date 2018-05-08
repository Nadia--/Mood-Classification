# Project Libraries
import hdf5_helper as hh
import genre_classifier as gc

# General Libraries
from unittest import TestCase
import numpy as np
import random



BASEDIR = '../../../../Thesis/data_sample/W/D/E'

class TestGenreClassifier(TestCase):
    def test_scrape_songs_by_genre(self):

        songs = hh.get_all_files(BASEDIR)[:5]

        positive_correct = []
        negative_correct = []

        for idx, song_loc in enumerate(songs):
            h5 = hh.open_h5_file_read(song_loc)
            almost_mfccs = hh.get_segments_timbre(h5)
            if idx == 1:
                negative_correct.append(almost_mfccs)
            else:
                positive_correct.append(almost_mfccs)
            h5.close()

        positive_examples, negative_examples = gc.scrape_songs_by_genre(BASEDIR, 'pop', 5)
        positive_shapes = [example.shape for example in positive_examples]

        self.assertAlmostEqual(len(positive_correct), len(positive_examples), "scrape songs by genre")
        self.assertAlmostEqual(len(negative_correct), len(negative_examples), "scrape songs by genre")

        self.assertTrue(positive_correct[0].shape in positive_shapes, "scrape songs by genre")
        self.assertFalse(negative_correct[0].shape in positive_shapes, "scrape songs by genre")

    def test_shuffle_examples(self):
        ordered = [i for i in range(10)]
        self.assertTrue(ordered[0]==0, "shuffle")
        self.assertTrue(ordered[9]==9, "shuffle")

        random.seed(0)
        shuffled = gc.shuffle_examples(ordered)
        self.assertTrue(shuffled[0]==7, "shuffle")
        self.assertTrue(shuffled[9]==6, "shuffle")
        self.assertTrue(shuffled[2]==1, "shuffle")

    def test_classifier_trial_evaluation_and_predictor_easy(self):
        positive_example1 = [[1,1], [1,2], [1,3], [1,4]]
        positive_example2 = [[1,5], [1,6], [1,7], [1,8]]
        negative_example1 = [[2,2], [2,2], [2,3], [2,4]]
        negative_example2 = [[2,5], [2,6], [2,7], [2,8]]

        positive_examples = [positive_example1, positive_example2]
        negative_examples = [negative_example1, negative_example2]

        positive_model, negative_model, train_accuracy, test_accuracy \
            = gc.run_trial(positive_examples, negative_examples, 0.5, num_components=1, covariance_type='diag')

        self.assertTrue(train_accuracy == 1, "dummy classifier example")
        self.assertTrue(test_accuracy == 1, "dummy classifier example")

        positive_example3 = [[1,9], [1,10], [1,11], [1,12]]
        is_positive = gc.is_in_genre_prediction(positive_model, negative_model, positive_example3)
        self.assertTrue(is_positive, "dummy classification prediction")

    def test_classifier_trial_evaluation_and_predictor_hard(self):
        # Deterministic
        np.random.seed(0) # used by our examples
        random.seed(5) # used by shuffling in run_trial

        random_positive = np.random.rand(10,4,2)
        random_negative = np.random.rand(10,4,2)

        positive_model, negative_model, train_accuracy, test_accuracy \
            = gc.run_trial(random_positive, random_negative, 0.5, num_components=1, covariance_type='diag')

        self.assertTrue(train_accuracy > 0.5, "hard classifier example")
        self.assertTrue(test_accuracy < 0.5, "hard classifier example")

        random_example = np.random.rand(4,2)
        is_positive = gc.is_in_genre_prediction(positive_model, negative_model, random_example)
        self.assertTrue(is_positive, "hard classification prediction")


