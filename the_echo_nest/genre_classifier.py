# Project Libraries
import hdf5_helper as hh

# General Libraries
import numpy as np
import random
from sklearn import mixture

"""
API for creating a binary classifier for a specific genre using MFCCs from TheEchoNest song data
"""

def scrape_songs_by_genre(basedir, genre, limit):
    """
    Returns the mfccs of songs that are in the genre, and outside of the genre

    :param basedir: the directory of songs we should classify
    :param genre: the genre we are looking to classify
    :param limit: the maximum number of songs within the directory that should be classified
    :return: mffcs of songs in the genre, mfccs of songs not in the genre
    """
    songs = hh.get_all_files(basedir)
    if limit:
        songs = songs[:limit]
    print("\n\nScraping %d songs for genre: %s" % (len(songs), genre))

    positive_examples = []
    negative_examples = []

    for song_loc in songs:
        h5 = hh.open_h5_file_read(song_loc)

        artist_tags = [term.decode('utf-8') for term in hh.get_artist_terms(h5)]
        almost_mfccs = hh.get_segments_timbre(h5)
        if genre in artist_tags:
            positive_examples.append(almost_mfccs)
        else:
            negative_examples.append(almost_mfccs)

        h5.close()

    return positive_examples, negative_examples


def shuffle_examples(examples):
    """
    Returns a shuffled version of examples array
    """
    perms = [i for i in range(len(examples))]
    random.shuffle(perms)
    examples_shuffled = [examples[i] for i in perms]
    return examples_shuffled


def is_in_genre_prediction(positive_model, negative_model, example_mfccs):
    """
    Returns whether the example is in the genre or not
    :param positive_model: the model describing songs that are in the genre
    :param negative_model: the model describing songs outside of the genre
    :param example_mfccs: the example we are classifying
    """
    pos_log_prob = positive_model.score(example_mfccs)
    neg_log_prob = negative_model.score(example_mfccs)
    if pos_log_prob > neg_log_prob:
        return True
    else:
        return False

def evaluate_classifier(positive_model, negative_model, positive_data, negative_data):
    """
    Evaluates a 2x2 matrix of actual vs predicted labels (in genre or out of genre) and returns prediction accuracy
    :param positive_model: the model describing songs that are in the genre
    :param negative_model: the model describing songs outside of the genre
    :param positive_data: mffcs of songs that are part of the genre
    :param negative_data: mffcs of songs that are outside of the genre
    :return: accuracy of classifier on the given examples
    """
    data = []
    data.extend(positive_data)
    data.extend(negative_data)

    num_positive = len(positive_data)

    results = np.zeros((2,2))
    for idx, song_mfccs in enumerate(data):
        is_in_genre = is_in_genre_prediction(positive_model, negative_model, song_mfccs)
        if idx < num_positive:
            if is_in_genre:
                results[0][0] += 1
            else:
                results[0][1] += 1
        else:
            if is_in_genre:
                results[1][0] += 1
            else:
                results[1][1] += 1

    print("Model Results: (row = real label, col = assigned label, order: positive, negative)")
    print(results)

    correct = np.sum([results[i][i] for i in range(len(results))])
    accuracy = correct / np.sum(results)
    print("Total Accuracy: %.2f" % accuracy)
    return accuracy


def run_trial(positive_examples, negative_examples, split, num_components, covariance_type):
    """
    Runs a single trial of creating and and evaluating a classifier
    Shuffles the data before every trial and splits it into training and testing data
    Returns the model of the classifier and its accuracies on traing and testing data

    :param positive_examples: mffcs of songs that are part of the genre
    :param negative_examples: mffcs of songs that are outside of the genre
    :param split: percent split in training vs testing data
    :param num_components: number of components in the gaussian mixture model
    :param covariance_type: the type of covariance in the gaussian mixture model
    """
    num_pos_training = round(split * len(positive_examples))
    num_neg_training = round(split * len(negative_examples))

    # Shuffle
    positive_examples_shuffled = shuffle_examples(positive_examples)
    negative_examples_shuffled = shuffle_examples(negative_examples)

    # Split Data into Training and Testing
    positive_training = positive_examples_shuffled[:num_pos_training]
    negative_training = negative_examples_shuffled[:num_neg_training]
    positive_testing = positive_examples_shuffled[num_pos_training:]
    negative_testing = negative_examples_shuffled[num_neg_training:]

    # Flattening Data
    positive_concatenated = [mfcc for song in positive_training for mfcc in song]
    negative_concatenated = [mfcc for song in negative_training for mfcc in song]

    # Training the Model
    positive_model = mixture.GaussianMixture(n_components=num_components, covariance_type=covariance_type)
    positive_model.fit(positive_concatenated)
    negative_model = mixture.GaussianMixture(n_components=num_components, covariance_type=covariance_type)
    negative_model.fit(negative_concatenated)

    # Evaluate on Training Data
    print("\nTraining Data Model Results")
    training_accuracy = evaluate_classifier(positive_model, negative_model, positive_training, negative_training)

    # Evaluate on Test Data
    print("\nTesting Data Model Results")
    testing_accuracy = evaluate_classifier(positive_model, negative_model, positive_testing, negative_testing)

    return positive_model, negative_model, training_accuracy, testing_accuracy


def learn_classifier(basedir, genre, split=0.5, num_trials=1, num_components=5, covariance_type='full', limit=None):
    """
    Divides up to limit songs in basedir by belonging to a genre or not
    Runs up to num_trials of creating and evaluating a classifier for those songs and prints average accuracy
    Returns the classifier with the best accuracy on test data

    :param basedir: the directory of songs we should classify
    :param genre: the genre we are looking to classify
    :param split: percent split in training vs testing data
    :param num_trials: the number of trials to run
    :param num_components: number of components in the gaussian mixture model
    :param covariance_type: the type of covariance in the gaussian mixture model
    :param limit: the maximum number of songs within the directory that should be classified
    :return:
    """
    positive_examples, negative_examples = scrape_songs_by_genre(basedir, genre, limit)

    avg_training_accuracy = 0
    avg_testing_accuracy = 0

    best_accuracy = 0
    best_positive_model = None
    best_negative_model = None

    for t in range(num_trials):
        print("\nTrial %d" % (t+1))
        positive_model, negative_model, training_accuracy, testing_accuracy \
            = run_trial(positive_examples, negative_examples, split, num_components, covariance_type)

        if testing_accuracy > best_accuracy:
            best_positive_model = positive_model
            best_negative_model = negative_model
            best_accuracy = testing_accuracy

        avg_training_accuracy += training_accuracy / num_trials
        avg_testing_accuracy += testing_accuracy / num_trials

    print("\nResults for genre: %s" % genre)
    print("Average Training Accuracy: %.2f" % avg_training_accuracy)
    print("Average Testing Accuracy: %.2f" % avg_testing_accuracy)

    return best_positive_model, best_negative_model


