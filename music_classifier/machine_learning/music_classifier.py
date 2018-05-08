# Project Libraries
import feature_extraction as fe
from feature_extraction import pFeats
from feature_extraction import pSTFT
import gaussian_binary_classifier as ml

# General Libraries
import numpy as np
import itertools

""" 
API for learning and tuning a binary mood classifier from song audio features
"""

class TuningParameters:
    def __init__(self):
        # Feature Extraction Parameters
        self.sampling_rate = [48000]
        self.stft = [pSTFT(2048, 512)]
        self.feat_comb = [pFeats(mfcc=True, spectral_centroid=True, spectral_flux=True)]
        self.num_mfccs = [20]

        # Gaussian Model Parameters
        self.num_components = [5]
        self.covariance_type = ['diag']

def prepare_examples_dictionary(song_to_label_dict_loc, label, label_dir, limit):
    """
    Returns the first limit number of positive and negative examples as a dictionary
    Also saves/loads data from cache, as appropriate
    """
    savefile = label_dir + '/' + 'examples' + '-' + limit
    examples_dictionary = fe.load_dictionary(savefile)

    if examples_dictionary is None:
        song_to_label_dict = fe.load_dictionary(song_to_label_dict_loc)

        positive_examples = []
        negative_examples = []

        for song, labels in song_to_label_dict.items():
            if len(positive_examples) >= limit and len(negative_examples) >= limit:
                break

            if label in labels:
                if len(positive_examples) < limit:
                    positive_examples.append(song)
            else:
                if len(negative_examples) < limit:
                    negative_examples.append(song)

        examples_dictionary['positive'] = positive_examples
        examples_dictionary['negative'] = negative_examples

        fe.write_dictionary(savefile, examples_dictionary)

    return examples_dictionary


def tune_classifier(song_to_label_dict_loc, label, dataset_name, tuning_parameters=TuningParameters(), num_trials=5, limit=None):
    dataset_dir = fe.prepare_directory([dataset_name])
    label_dir = fe.prepare_directory([dataset_dir, label + '-' + limit])
    examples_dictionary = prepare_examples_dictionary(song_to_label_dict_loc, label, label_dir, limit)
    examples = examples_dictionary['positive'] + examples_dictionary['negative']

    print("Obtained Positive and Negative Examples from Dataset")

    for stft_parameters in tuning_parameters.stft:
        stft_dir = fe.prepare_directory([label_dir, stft_parameters.dirname()])

        fe.prepare_features(stft_dir, examples, tuning_parameters.feat_comb, tuning_parameters.num_mfccs)
        print("Extracted all Features for STFT parameters: %s" % stft_parameters.dirname())

        for feature_comb in tuning_parameters.feat_comb:


            if feature_comb.mfcc:
                for num_mfccs in tuning_parameters.num_mfccs:
                    mfccs_dict = load_feature(stft_dir, "MFCC", num_mfccs)

            if feature_comb.spectral_centroid:
                spectral_centroids_dict = load_feature(stft_dir, "SPECT_CENT", "default")

            if feature_comb.spectra_flux:
                spectral_flux_dict = load_feature(stft_dir, "SPECT_FLUX", "default")

            ...

def classify_examples(mood, video_ids, video_ids_to_moods):
    """ Split examples into positive (have label) and negative (do not have label) """
    positive_video_ids = []
    negative_video_ids = []

    for video_id in video_ids:
        moods = video_ids_to_moods[video_id]
        if mood in moods:
            positive_video_ids.append(video_id)
        else:
            negative_video_ids.append(video_id)

    return positive_video_ids, negative_video_ids


def classifier_tuning_while_learning(positive_examples, negative_examples, num_trials, num_components_variables,
                          covariance_type_variables):
    """ Method to run classifiers with various Gaussian parameters to see which will perform the best """
    best_average_accuracy = 0
    best_positive_model = None
    best_negative_model = None
    best_actual_accuracy = 0

    accuracies = np.zeros((len(num_components_variables), len(covariance_type_variables)))

    for nc_idx, num_components in enumerate(num_components_variables):
        for ct_idx, covariance_type in enumerate(covariance_type_variables):

            print("\nRunning classifier for: \n%d components, \n%s covariance type" % (num_components, covariance_type))

            positive_model, negative_model, best_accuracy, average_accuracy = \
                ml.learn_classifier(positive_examples, negative_examples, num_trials=num_trials,
                                    num_components=num_components, covariance_type=covariance_type)
            accuracies[nc_idx][ct_idx] = average_accuracy

            if average_accuracy > best_average_accuracy:
                best_positive_model = positive_model
                best_negative_model = negative_model
                best_actual_accuracy = best_accuracy

    return best_positive_model, best_negative_model, best_actual_accuracy, accuracies,


def learn_classifier(video_ids_to_moods, mood, feats_file, num_trials=1, num_components_variables=[5],
                     covariance_type_variables=['diag'], limit=None, extract_features=False):
    """
    Learns a classifier for specified mood, evaluates it on training and testing data, returns best model of several trials

    :param video_ids_to_moods: dictionary mapping video_ids to list of moods
    :param mood: mood we are classifying
    :param feats_file: file to save/load the features corresponding to video_ids
    :param num_trials: the number of trials to run for each set of parameters
    :param num_components_variables: an array of values for number_components parameter
    :param covariance_type_variables: an array of values for covariance_type parameter
    :param limit: max number of video_ids to work with
    :param extract_features: whether to extract features (or just load them from file)
    """

    if extract_features:
        video_ids = itertools.islice(video_ids_to_moods.keys(), limit)
        print("Extracting Features for %d songs..." % limit)
        extract_and_save_features(video_ids, feats_file)

    # Load from File
    video_ids_to_features = load_features(feats_file)
    video_ids = video_ids_to_features.keys()
    print("Obtained Features from File")

    positive_video_ids, negative_video_ids = classify_examples(mood, video_ids, video_ids_to_moods)

    positive_examples = [np.swapaxes(video_ids_to_features[video_id], 0, 1) for video_id in positive_video_ids]
    negative_examples = [np.swapaxes(video_ids_to_features[video_id], 0, 1) for video_id in negative_video_ids]

    positive_model, negative_model, model_accuracy, accuracies = \
        classifier_tuning_while_learning(positive_examples, negative_examples, num_trials, num_components_variables, covariance_type_variables)

    print("num components parameters: %s" % str(num_components_variables))
    print("covariance type parameters: %s" % str(covariance_type_variables))
    print("\nTuning parameter accuracies:")
    print(accuracies)

    print("Returning best model of the highest accuracy parameter run")
    print("Its testing accuracy is %.2f" % model_accuracy)

    return positive_model, negative_model

def predict_mood(audio_file_name, mood_model):
    """ Given the location of an song file and a mood model, predicts whether the song has that mood """
    positive_model, negative_model = mood_model
    audio, sr = fe.load_audio_file(audio_file_name)
    features = np.swapaxes(fe.extract_features(audio, sr), 0, 1)
    return ml.is_in_genre_prediction(positive_model, negative_model, features)


