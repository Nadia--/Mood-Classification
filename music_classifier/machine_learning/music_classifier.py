# Project Libraries
import feature_extraction as fe
from feature_extraction import pFeats
from feature_extraction import pSTFT
import gaussian_binary_classifier as gbc

# General Libraries
import numpy as np
import logging

""" 
API for learning and tuning a binary mood classifier from song audio features
"""

LOGFILE = "./../data/logs/log_results"


class TuningParameters:
    def __init__(self):
        # Feature Extraction Parameters
        self.stft = [pSTFT(.1, 0.25)]
        self.feat_comb = [pFeats(mfcc=True, spectral_centroid=True, spectral_flux=True)]
        self.num_mfccs = [20]

        # Gaussian Model Parameters
        self.num_components = [1]
        self.covariance_type = ['spherical']

    def __repr__(self):
        str_rep = "\nTuning Parameters:"
        str_rep += "\nSTFT parameters: " + str(self.stft)
        str_rep += "\nFeature Combinations: " + str(self.feat_comb)
        str_rep += "\nNum MFCCs: " + str(self.num_mfccs)
        str_rep += "\nGaussian Num Components " + str(self.num_components)
        str_rep += "\nGaussian Covariance Type: " + str(self.covariance_type)
        str_rep += '\n'
        return str_rep


def cache_examples_dictionary(song_to_label_dict_loc, label, label_dir, limit):
    """
    Returns the first limit number of positive and negative examples as a dictionary
    Also saves/loads data from cache, as appropriate
    """
    savefile = label_dir + '/' + 'examples'
    examples_dictionary = fe.read_dictionary(savefile)


    if examples_dictionary is None:
        song_to_label_dict = fe.read_dictionary(song_to_label_dict_loc)

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

        if len(positive_examples) != limit or len(negative_examples) != limit:
            logging.warning("Requested %d positive and negative examples, but data only %d positive and %d negative in data!" %
                            (limit, len(positive_examples), len(negative_examples)))

        examples_dictionary = {}
        examples_dictionary['positive'] = positive_examples
        examples_dictionary['negative'] = negative_examples

        fe.write_dictionary(savefile, examples_dictionary)

    print("\nFor this label and data there are:")
    print("%d positive examples" % len(examples_dictionary['positive']))
    print("%d negative examples" % len(examples_dictionary['negative']))

    return examples_dictionary


def maybe_dictionary(bool, feature_dict_name):
    if bool:
        return fe.read_feats_dictionary(feature_dict_name)
    return None


def concatenate_features(examples, mfcc_dict, spectral_flux_dict, spectral_centroids_dict):
    example_feats = []

    for song in examples:
        feats = [None] * 3

        if mfcc_dict is not None:
            feats[0] = mfcc_dict[song]
        if spectral_flux_dict is not None:
            feats[1] = spectral_flux_dict[song]
        if spectral_centroids_dict is not None:
            feats[2] = spectral_centroids_dict[song]

        feats = [feat for feat in feats if feat is not None]
        example_features = np.concatenate(tuple(feats))
        example_feats.append(np.swapaxes(example_features, 0, 1))

    return example_feats



def tune_classifier(music_data_dir, dict_name, label, dataset_name, tuning_parameters=TuningParameters(), num_trials=5, limit=None):
    """
    THIS ONLY WORKS ON SMALL DATA SAMPLES because it extracts all possible features and saves them to drive for purposes of caching work

    :param music_data_dir:
    :param dict_name:
    :param label:
    :param dataset_name:
    :param tuning_parameters:
    :param num_trials:
    :param limit:
    :return:
    """
    dataset_dir = fe.cache_directory(dataset_name)
    label_dir = fe.cache_directory(label + '-' + str(limit), base=dataset_dir)
    examples_dictionary = cache_examples_dictionary(music_data_dir + 'dictionaries/' + dict_name, label, label_dir, limit)
    examples = examples_dictionary['positive'] + examples_dictionary['negative']
    print("Obtained Positive and Negative Examples from Dataset\n")

    best_average_accuracy = 0
    best_positive_model = None
    best_negative_model = None
    best_actual_accuracy = 0

    overall_accuracies = np.zeros((len(tuning_parameters.stft), len(tuning_parameters.feat_comb), len(tuning_parameters.num_mfccs),
                                   len(tuning_parameters.num_components), len(tuning_parameters.covariance_type)))

    shape = overall_accuracies.shape
    total_permuations =  shape[0] * shape[1] * shape[2]
    counter = 0

    for sp_idx, stft_parameters in enumerate(tuning_parameters.stft):
        stft_dir = fe.cache_directory(stft_parameters.dir_name(), base=label_dir)

        fe.extract_features_to_cache(stft_dir, stft_parameters, examples, music_data_dir, tuning_parameters.feat_comb, tuning_parameters.num_mfccs)
        print("Done Extracting and Writing Features for STFT parameters: %s" % stft_parameters.dir_name())

        for fc_idx, feature_comb in enumerate(tuning_parameters.feat_comb):

            spectral_centroids_dict = maybe_dictionary(feature_comb.spectral_centroid, fe.feature_dict_name(stft_dir, "SPECT_CENT", "default"))
            spectral_flux_dict = maybe_dictionary(feature_comb.spectral_flux, fe.feature_dict_name(stft_dir, "SPECT_FLUX", "default"))
            for nm_idx, num_mfccs in enumerate(tuning_parameters.num_mfccs):
                mfcc_dict = maybe_dictionary(feature_comb.mfcc, fe.feature_dict_name(stft_dir, "MFCC", str(num_mfccs)))

                print("Tuning Progress: %d%%" % (counter/total_permuations * 100))
                # TODO: including tuning progress for gaussian classifier too?

                positive_example_feats = concatenate_features(examples_dictionary['positive'], mfcc_dict, spectral_flux_dict, spectral_centroids_dict)
                negative_example_feats = concatenate_features(examples_dictionary['negative'], mfcc_dict, spectral_flux_dict, spectral_centroids_dict)

                positive_model, negative_model, best_accuracy, accuracies = \
                    gbc.tune_gaussian_classifier(positive_example_feats,
                                                 negative_example_feats,
                                                 tuning_parameters.num_components,
                                                 tuning_parameters.covariance_type,
                                                 num_trials)

                counter += 1

                overall_accuracies[sp_idx][fc_idx][nm_idx] = accuracies

                if np.max(accuracies) > best_average_accuracy:
                    best_positive_model = positive_model
                    best_negative_model = negative_model
                    best_actual_accuracy = best_accuracy

                # If we're not using mfccs as a feature, no need to iterate over number of mfccs parameters
                if mfcc_dict is None:
                    counter += len(tuning_parameters.feat_comb) - 1
                    break



    print("\nData: %s" % dict_name)
    print("Label: %s, Limit: %d" %(label, limit))
    print("Trials: %d" % num_trials)
    print(tuning_parameters)
    print("Average accuracies over tuning parameters:\n")
    print(overall_accuracies)

    print("Best model accuracy from highest averaging parameter run is %.2f" % best_actual_accuracy)

    write_results_to_log(dict_name, label, limit, tuning_parameters, num_trials, overall_accuracies, best_actual_accuracy)

    return best_positive_model, best_negative_model, best_actual_accuracy, overall_accuracies


def write_results_to_log(dict_name, label, limit, tuning_parameters, num_trials, overall_accuracies, best_accuracy):
    with open(LOGFILE, 'a') as fp:
        fp.write("\n\nData: %s" % dict_name)
        fp.write("\nLabel: %s, Limit: %d" %(label, limit))
        fp.write("\nTrials: %d" % num_trials)
        fp.write("\n" + str(tuning_parameters))
        fp.write("\nAverage accuracies over tuning parameters:\n")
        fp.write(str(overall_accuracies))
        fp.write("\n\nBest model accuracy from highest averaging parameter run is %.2f" % best_accuracy)
        fp.write("\n\n#######")

# TODO: create an online version without tuning and caching and etc, allow features to be extracted while learning

# def predict_mood(audio_file_name, mood_model):
#     #TODO: needs updating
#
#     """ Given the location of an song file and a mood model, predicts whether the song has that mood """
#     positive_model, negative_model = mood_model
#     audio, sr = fe.load_audio_file(audio_file_name)
#     features = np.swapaxes(fe.extract_features(audio, sr), 0, 1)
#     return ml.is_in_genre_prediction(positive_model, negative_model, features)




