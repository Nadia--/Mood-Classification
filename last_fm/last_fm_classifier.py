# Project Libraries
import last_fm_downloader as fm_dl
import feature_extraction as fe
import classifier as ml
import last_fm_api as fm

# General Libraries
import numpy as np
import json
import itertools

""" 
API for learning and tuning a binary mood classifier from song audio features
"""


def extract_features(video_ids):
    """ Extracts audio features from audio tracks corresponding to YouTube video ids """
    video_ids_to_features = {}

    counter = 0
    for video_id in video_ids:
        counter += 1
        print(counter)
        audio, sr = fe.get_audio(video_id)
        feats = fe.extract_features(audio, sr)
        video_ids_to_features[video_id] = feats

    return video_ids_to_features


def extract_and_save_features(video_ids, filename):
    """ Extract audio features and save to file """
    video_ids_to_features = extract_features(video_ids)
    video_ids_to_features_serialized = {key: value.tolist() for (key, value) in video_ids_to_features.items()}

    dir_name = fm.BASE_DIRECTORY + filename
    with open(dir_name, 'w') as fp:
        json.dump(video_ids_to_features_serialized, fp)


def load_features(filename):
    """ Load saved audio features from file """
    video_ids_to_features_serialized = fm.load_dictionary(filename)
    video_ids_to_features = {key: np.array(value) for (key, value) in video_ids_to_features_serialized.items()}
    return video_ids_to_features


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
    """ Method to run classifiers with various parameters to see which will perform the best """
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


